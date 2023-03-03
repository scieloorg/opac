# coding: utf-8
import json
import logging
import socket
from uuid import uuid4

import flask_admin as admin
import flask_login as login
from flask import (
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_admin.actions import action
from flask_admin.contrib import mongoengine, sqla
from flask_admin.contrib.mongoengine.tools import parse_like_term
from flask_admin.form import Select2Field
from flask_admin.model.form import InlineFormAdmin
from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __
from jinja2 import Markup
from legendarium.formatter import descriptive_short_format
from mongoengine import (
    EmailField,
    EmbeddedDocumentField,
    ReferenceField,
    StringField,
    URLField,
)
from mongoengine.errors import NotUniqueError
from opac_schema.v1.models import Article, AuditLogEntry, Issue, Journal, Pages, Sponsor
from webapp import choices, controllers, custom_filters, models
from webapp.admin import custom_fields, forms
from webapp.admin.ajax import CustomQueryAjaxModelLoader
from webapp.admin.custom_filters import (
    CustomFilterConverter,
    CustomFilterConverterSqla,
    get_flt,
)
from webapp.admin.custom_widget import CKEditorField
from webapp.utils import (
    fix_journal_last_issue,
    get_timed_serializer,
    migrate_page_content,
)
from wtforms.fields import SelectField

ACTION_PUBLISH_CONFIRMATION_MSG = _(
    "Tem certeza que quer publicar os itens selecionados?"
)
ACTION_UNPUBLISH_CONFIRMATION_MSG = _(
    "Tem certeza que quer despublicar os itens selecionados?"
)
ACTION_REBUILD_CONFIRMATION_MSG = _(
    "Tem certeza que quer reconstruir os artigos selecionados?"
)
ACTION_SEND_EMAIL_CONFIRMATION_MSG = _(
    "Tem certeza que quer enviar email de confirmação aos usuários selecionados?"
)
ACTION_UNHIDE_FULL_TEXT_CONFIRMATION_MSG = _(
    "Tem certeza que deseja disponibilizar o texto completo?"
)
ACTION_HIDE_FULL_TEXT_CONFIRMATION_MSG = _(
    "Tem certeza que deseja indisponibilizar o texto completo?"
)

logger = logging.getLogger(__name__)


class AdminIndexView(admin.AdminIndexView):
    @admin.expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        counts = {
            "journals_total_count": controllers.count_elements_by_type_and_visibility(
                "journal", public_only=False
            ),
            "journals_public_count": controllers.count_elements_by_type_and_visibility(
                "journal", public_only=True
            ),
            "issues_total_count": controllers.count_elements_by_type_and_visibility(
                "issue", public_only=False
            ),
            "issues_public_count": controllers.count_elements_by_type_and_visibility(
                "issue", public_only=True
            ),
            "articles_total_count": controllers.count_elements_by_type_and_visibility(
                "article", public_only=False
            ),
            "articles_public_count": controllers.count_elements_by_type_and_visibility(
                "article", public_only=True
            ),
            "news_total_count": controllers.count_elements_by_type_and_visibility(
                "news"
            ),
            "sponsors_total_count": controllers.count_elements_by_type_and_visibility(
                "sponsor"
            ),
            "pressrelease_total_count": controllers.count_elements_by_type_and_visibility(
                "pressrelease"
            ),
        }
        self._template_args["counts"] = counts
        return super(AdminIndexView, self).index()

    @admin.expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        form = forms.LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user_email = form.data["email"]
            user = controllers.get_user_by_email(user_email)
            if not user.email_confirmed:
                return self.render("admin/auth/unconfirm_email.html")
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))

        self._template_args["form"] = form

        return self.render("admin/auth/login.html")

    @admin.expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))

    @admin.expose("/confirm/<token>", methods=("GET",))
    def confirm_email(self, token):
        try:
            ts = get_timed_serializer()
            email = ts.loads(
                token,
                salt="email-confirm-key",
                max_age=current_app.config["TOKEN_MAX_AGE"],
            )
        except (
            Exception
        ):  # possiveis exceções: https://pythonhosted.org/itsdangerous/#exceptions
            # qualquer exeção invalida a operação de confirmação
            abort(404)  # melhorar mensagem de erro para o usuário

        user = controllers.get_user_by_email(email=email)
        if not user:
            abort(404, _("Usuário não encontrado"))

        controllers.set_user_email_confirmed(user)
        flash(_("Email: %(email)s confirmado com sucesso!", email=user.email))
        return redirect(url_for(".index"))

    @admin.expose("/reset/password", methods=("GET", "POST"))
    def reset(self):
        form = forms.EmailForm(request.form)

        if admin.helpers.validate_form_on_submit(form):
            user = controllers.get_user_by_email(email=form.data["email"])
            if not user:
                abort(404, _("Usuário não encontrado"))
            if not user.email_confirmed:
                return self.render("admin/auth/unconfirm_email.html")

            was_sent, error_msg = user.send_reset_password_email()
            if was_sent:
                flash(
                    _(
                        "Enviamos as instruções para recuperar a senha para: %(email)s",
                        email=user.email,
                    )
                )
            else:
                flash(
                    _(
                        "Ocorreu um erro no envio das instruções por email para: %(email)s. Erro: %(error)s",
                        email=user.email,
                        error=error_msg,
                    ),
                    "error",
                )

            return redirect(url_for(".index"))

        self._template_args["form"] = form
        return self.render("admin/auth/reset.html")

    @admin.expose("/reset/password/<token>", methods=("GET", "POST"))
    def reset_with_token(self, token):
        try:
            ts = get_timed_serializer()
            email = ts.loads(
                token, salt="recover-key", max_age=current_app.config["TOKEN_MAX_AGE"]
            )
        except Exception:
            abort(404)

        form = forms.PasswordForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = controllers.get_user_by_email(email=email)
            if not user.email_confirmed:
                return self.render("admin/auth/unconfirm_email.html")

            controllers.set_user_password(user, form.password.data)
            flash(_("Nova senha salva com sucesso!!"))
            return redirect(url_for(".index"))

        self._template_args["form"] = form
        self._template_args["token"] = token
        return self.render("admin/auth/reset_with_token.html")


class UserAdminView(sqla.ModelView):
    page_size = 20
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    form_excluded_columns = ("password", "email_confirmed")
    column_filters = ["email"]

    def after_model_change(self, form, model, is_created):
        if is_created:
            try:
                was_sent, error_msg = model.send_confirmation_email()
            except (ValueError, socket.error) as e:
                was_sent = False
                error_msg = e.message
            # Enviamos o email de confirmação para o usuário.
            if was_sent:
                flash(
                    _(
                        "Enviamos o email de confirmação para: %(email)s",
                        email=model.email,
                    )
                )
            else:
                flash(
                    _(
                        "Ocorreu um erro no envio do email de confirmação para: %(email)s %(error_msg)s",
                        email=model.email,
                        error_msg=error_msg,
                    ),
                    "error",
                )

    def is_accessible(self):
        return login.current_user.is_authenticated

    @action(
        "confirm_email",
        _("Enviar email de confirmação"),
        ACTION_SEND_EMAIL_CONFIRMATION_MSG,
    )
    def action_send_confirm_email(self, ids):
        try:
            query = models.User.query.filter(models.User.id.in_(ids))
            count = 0
            for user in query.all():
                was_sent, error_msg = user.send_confirmation_email()
                if was_sent:
                    count += 1
                    flash(
                        _(
                            "Enviamos o email de confirmação para: %(email)s",
                            email=user.email,
                        )
                    )
                else:
                    flash(
                        _(
                            "Ocorreu um erro no envio do email de confirmação para: %(email)s",
                            email=user.email,
                        ),
                        "error",
                    )

            flash(_("%(count)s usuários foram notificados com sucesso!", count=count))
        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro no envio do emails de confirmação. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )


class AssetsMixin(object):
    form_choices = {
        "language": models.LANGUAGES_CHOICES,
    }
    column_searchable_list = [
        "name",
    ]

    filter_converter = CustomFilterConverterSqla()

    def is_accessible(self):
        return login.current_user.is_authenticated


class FileAdminView(AssetsMixin, sqla.ModelView):
    def _path_formatter(self, context, model, name):
        return Markup(
            "<a href='{url}' target='_blank'>Open</a>".format(
                url=model.get_absolute_url
            )
        )

    column_list = ("name", "path", "language")
    column_formatters = {
        "path": _path_formatter,
    }
    column_filters = ["language"]

    form_overrides = {"path": custom_fields.MediaFileUploadField}

    column_labels = dict(
        name=__("Nome"),
        path=__("Link"),
        language=__("Idioma"),
    )

    def search_placeholder(self):
        if self.column_searchable_list:
            return ", ".join(
                str(self.column_labels.get(col, col))
                for col in self.column_searchable_list
            )


class ImageAdminView(AssetsMixin, sqla.ModelView):
    def _path_formatter(self, context, model, name):
        return Markup(
            "<a href='{url}' target='_blank'>Open</a>".format(
                url=model.get_absolute_url
            )
        )

    def _preview_formatter(self, context, model, name):
        if not model.path:
            return ""
        else:
            return Markup(
                "<img src='{url}'>".format(url=model.get_thumbnail_absolute_url)
            )

    column_list = ("name", "preview", "path", "language")
    column_formatters = {
        "preview": _preview_formatter,
        "path": _path_formatter,
    }
    column_filters = ["language"]

    form_overrides = {"path": custom_fields.MediaImageUploadField}

    column_labels = dict(
        name=__("Nome"),
        preview=__("Previsualização"),
        path=__("Link"),
        language=__("Idioma"),
    )

    def search_placeholder(self):
        if self.column_searchable_list:
            return ", ".join(
                str(self.column_labels.get(col, col))
                for col in self.column_searchable_list
            )


class OpacBaseAdminView(mongoengine.ModelView):
    page_size = 20
    can_create = False
    can_edit = False
    can_delete = False
    create_modal = True
    edit_modal = True
    can_view_details = True
    allowed_search_types = (
        StringField,
        URLField,
        EmailField,
        EmbeddedDocumentField,
        ReferenceField,
    )
    filter_converter = CustomFilterConverter()
    object_id_converter = str

    def _search(self, query, search_term):
        op, term = parse_like_term(search_term)

        criteria = None

        for field in self._search_fields:
            flt = get_flt(field, term, op)

            if criteria is None:
                criteria = flt
            else:
                criteria |= flt
        return query.filter(criteria)

    def is_accessible(self):
        return login.current_user.is_authenticated


class NewsAdminView(OpacBaseAdminView):
    can_create = False
    can_edit = False
    can_delete = False
    page_size = 30

    def _url_formatter(self, context, model, name):
        return Markup("<a href='{url}' target='_blank'>Open</a>".format(url=model.url))

    def _preview_formatter(self, context, model, name):
        if not model.image_url:
            return ""
        else:
            return Markup("<img src='{url}'>".format(url=model.image_url))

    def _preview_date_format(self, context, model, name):
        return custom_filters.datetimefilter(model.publication_date)

    column_formatters = {
        "url": _url_formatter,
        "image_url": _preview_formatter,
        "publication_date": _preview_date_format,
    }

    form_overrides = dict(
        language=Select2Field,
    )
    form_args = dict(
        language=dict(choices=choices.LANGUAGES_CHOICES),
    )
    column_exclude_list = (
        "_id",
        "description",
    )
    column_filters = ["language"]
    column_searchable_list = [
        "_id",
        "title",
        "description",
    ]


class SponsorAdminView(OpacBaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    create_modal = False
    edit_modal = False
    can_view_details = True
    column_exclude_list = ("_id",)
    column_searchable_list = ("name",)

    column_labels = dict(
        order=__("Ordem"),
        name=__("Nome"),
        url=__("URL"),
        logo_url=__("URL da logomarca"),
    )

    def on_model_change(self, form, model, is_created):
        # é necessario definir um valor para o campo ``_id`` na criação.
        if is_created:
            model._id = str(uuid4().hex)

    def handle_view_exception(self, exc):
        if isinstance(exc, NotUniqueError):
            flash(_("Financiador com Ordem ou Nome já cadastrado!"), "error")
            return True
        return super(SponsorAdminView, self).handle_view_exception(exc)


class CollectionAdminView(OpacBaseAdminView):
    can_edit = True
    edit_modal = True
    form_excluded_columns = ("acronym", "metrics")
    column_exclude_list = [
        "_id",
        "about",
        "home_logo_pt",
        "home_logo_es",
        "home_logo_en",
        "header_logo_pt",
        "header_logo_es",
        "header_logo_en",
        "menu_logo_pt",
        "menu_logo_es",
        "menu_logo_en",
        "logo_footer",
        "logo_drop_menu",
    ]
    column_labels = dict(
        name=__("Nome"),
        about=__("Acerca de"),
        acronym=__("Acrônimo"),
        address1=__("Endereço principal"),
        address2=__("Endereço secundário"),
        home_logo_pt=__("Logo da Home (PT)"),
        home_logo_en=__("Logo da Home (EN)"),
        home_logo_es=__("Logo da Home (ES)"),
        header_logo_pt=__("Logo do cabeçalho (PT)"),
        header_logo_en=__("Logo do cabeçalho (EN)"),
        header_logo_es=__("Logo do cabeçalho (ES)"),
        menu_logo_pt=__("Logo do menu (PT)"),
        menu_logo_en=__("Logo do menu (ES)"),
        menu_logo_es=__("Logo do menu (ES)"),
        logo_drop_menu=__("Logo do menu (drop)"),
        logo_footer=__("Logo do rodapé"),
    )

    inline_models = (InlineFormAdmin(Sponsor),)


class JournalAdminView(OpacBaseAdminView):
    can_edit = True

    form_columns = ("enable_contact", "scimago_id", "is_public", "logo_url")

    form_overrides = {
        "enable_contact": custom_fields.RequiredBooleanField,
        "is_public": custom_fields.RequiredBooleanField,
    }

    column_filters = [
        "current_status",
        "index_at",
        "is_public",
        "unpublish_reason",
        "scimago_id",
    ]

    column_searchable_list = [
        "_id",
        "title",
        "title_iso",
        "short_title",
        "print_issn",
        "eletronic_issn",
        "acronym",
    ]

    column_exclude_list = [
        "_id",
        "jid",
        "title_slug",
        "timeline",
        "subject_categories",
        "study_areas",
        "social_networks",
        "title_iso",
        "short_title",
        "subject_descriptors",
        "copyrighter",
        "online_submission_url",
        "cover_url",
        "logo_url",
        "previous_journal_ref",
        "publisher_name",
        "publisher_country",
        "publisher_state",
        "publisher_city",
        "publisher_address",
        "publisher_telephone",
        "mission",
        "index_at",
        "sponsors",
        "issue_count",
        "other_titles",
        "print_issn",
        "eletronic_issn",
        "unpublish_reason",
        "url_segment",
    ]

    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime("%Y-%m-%d %H:%M:%S"),
        updated=lambda v, c, m, p: m.created.strftime("%Y-%m-%d %H:%M:%S"),
        scielo_issn=lambda v, c, m, p: "%s\n%s"
        % (m.print_issn or "", m.eletronic_issn or ""),
    )

    column_labels = dict(
        jid=__("Id Periódico"),
        collection=__("Coleção"),
        timeline=__("Linha do tempo"),
        subject_categories=__("Categorias de assunto"),
        study_areas=__("Áreas de estudo"),
        social_networks=__("Redes sociais"),
        title=__("Título"),
        title_iso=__("Título ISO"),
        short_title=__("Título curto"),
        created=__("Criado"),
        updated=__("Atualizado"),
        acronym=__("Acrônimo"),
        scielo_issn=__("ISSN SciELO"),
        print_issn=__("ISSN impresso"),
        eletronic_issn=__("ISSN eletrônico"),
        subject_descriptors=__("Descritores de assunto"),
        online_submission_url=__("Url da submissão online"),
        cover_url=__("Url do capa"),
        logo_url=__("Url do logotipo"),
        other_titles=__("Outros títulos"),
        publisher_name=__("Nome da editora"),
        publisher_country=__("País da editora"),
        publisher_state=__("Estado da editora"),
        publisher_city=__("Cidade da editora"),
        publisher_address=__("Endereço da editora"),
        publisher_telephone=__("Telefone da editora"),
        mission=__("Missão"),
        index_at=__("No índice"),
        sponsors=__("Patrocinadores"),
        previous_journal_ref=__("Ref periódico anterior"),
        current_status=__("Situação atual"),
        issue_count=__("Total de números"),
        is_public=__("Publicado?"),
        unpublish_reason=__("Motivo de despublicação"),
        url_segment=__("Segmento de URL"),
    )

    @action("publish", _("Publicar"), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_journal_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_("Periódico(s) publicado(s) com sucesso!!"))
        except Exception:
            flash(_("Ocorreu um erro tentando publicar o(s) periódico(s)!!"), "error")

    def unpublish_journals(self, ids, reason):
        try:
            controllers.set_journal_is_public_bulk(ids, False, reason)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_("Periódico(s) despublicado com sucesso!!"))
        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro tentando despublicar o(s) periódico(s)!!. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    # Veja: https://github.com/scieloorg/opac/issues/411#issuecomment-265515533
    @action(
        "unpublish_default",
        _("Despublicar por %s" % choices.UNPUBLISH_REASONS[0]),
        ACTION_UNPUBLISH_CONFIRMATION_MSG,
    )
    def unpublish_default(self, ids):
        self.unpublish_journals(ids, choices.UNPUBLISH_REASONS[0])


class IssueAdminView(OpacBaseAdminView):
    column_filters = [
        "journal",
        "volume",
        "number",
        "type",
        "start_month",
        "end_month",
        "year",
        "is_public",
        "unpublish_reason",
    ]
    column_searchable_list = ["iid", "journal", "volume", "number", "label"]
    column_exclude_list = [
        "_id",
        "iid",
        "sections",
        "cover_url",
        "suppl_text",
        "spe_text",
        "start_month",
        "end_month",
        "order",
        "label",
        "order",
        "unpublish_reason",
        "url_segment",
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime("%Y-%m-%d %H:%M:%S"),
        updated=lambda v, c, m, p: m.created.strftime("%Y-%m-%d %H:%M:%S"),
    )
    column_labels = dict(
        iid=__("Id Número"),
        journal=__("Periódico"),
        sections=__("Seções"),
        cover_url=__("Url da capa"),
        volume=__("Volume"),
        number=__("Número"),
        created=__("Criado"),
        updated=__("Atualizado"),
        type=__("Tipo"),
        suppl_text=__("Texto do suplemento"),
        spe_text=__("Texto do especial"),
        start_month=__("Mês inicial"),
        end_month=__("Mês final"),
        year=__("Ano"),
        label=__("Etiqueta"),
        order=__("Ordem"),
        is_public=__("Publicado?"),
        unpublish_reason=__("Motivo de despublicação"),
        pid=__("PID"),
        url_segment=__("Segmento de URL"),
    )

    @action("publish", _("Publicar"), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_issue_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_("Número(s) publicado(s) com sucesso!!"))
        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro tentando publicar o(s) número(s)!!. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    def unpublish_issues(self, ids, reason):
        try:
            controllers.set_issue_is_public_bulk(ids, False, reason)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_("Número(s) despublicado(s) com sucesso!!"))
        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro tentando despublicar o(s) número(s)!!. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    # Veja: https://github.com/scieloorg/opac/issues/411#issuecomment-265515533
    @action(
        "unpublish_default",
        _("Despublicar por %s" % choices.UNPUBLISH_REASONS[0]),
        ACTION_UNPUBLISH_CONFIRMATION_MSG,
    )
    def unpublish_default(self, ids):
        self.unpublish_issues(ids, choices.UNPUBLISH_REASONS[0])


class ArticleAdminView(OpacBaseAdminView):
    column_filters = [
        "issue",
        "journal",
        "is_aop",
        "is_public",
        "unpublish_reason",
        "display_full_text",
    ]

    column_searchable_list = ["aid", "issue", "journal", "title", "domain_key"]

    column_exclude_list = [
        "_id",
        "aid",
        "section",
        "is_aop",
        "htmls",
        "domain_key",
        "xml",
        "unpublish_reason",
        "translated_titles",
        "sections",
        "pdfs",
        "languages",
        "original_language",
        "created",
        "abstract",
        "authors",
        "order",
        "abstract_languages",
        "elocation",
        "fpage",
        "lpage",
        "url_segment",
    ]

    column_details_exclude_list = [
        "xml",
    ]

    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime("%Y-%m-%d %H:%M:%S"),
        updated=lambda v, c, m, p: m.created.strftime("%Y-%m-%d %H:%M:%S"),
    )

    column_labels = dict(
        aid=__("Id Artigo"),
        issue=__("Número"),
        journal=__("Periódico"),
        title=__("Título"),
        section=__("Seção"),
        is_aop=__("É Ahead of Print?"),
        created=__("Criado"),
        updated=__("Atualizado"),
        htmls=__("HTML's"),
        domain_key=__("Chave de domínio"),
        is_public=__("Publicado?"),
        unpublish_reason=__("Motivo de despublicação"),
        url_segment=__("Segmento de URL"),
        pid=__("PID"),
        original_language=__("Idioma original"),
        translated_titles=__("Idiomas das traduções"),
        sections=__("Seções"),
        authors=__("Autores"),
        abstract=__("Resumo"),
        order=__("Ordem"),
        doi=__("DOI"),
        languages=__("Idiomas"),
        abstract_languages=__("Idiomas dos resumos"),
        display_full_text=__("Texto completo disponível?"),
    )

    @action(
        "set_full_text_unavailable",
        _("Indisponibilizar texto completo"),
        ACTION_HIDE_FULL_TEXT_CONFIRMATION_MSG,
    )
    def set_full_text_unavailable(self, ids):
        try:
            controllers.set_article_display_full_text_bulk(ids, display=False)
            flash(_("Texto completo foi indisponibilizado"))

        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro ao tentar indisponibilizar completo. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    @action(
        "set_full_text_available",
        _("Disponibilizar texto completo"),
        ACTION_UNHIDE_FULL_TEXT_CONFIRMATION_MSG,
    )
    def set_full_text_available(self, ids):
        try:
            controllers.set_article_display_full_text_bulk(ids, display=True)
            flash(_("Texto completo foi disponibilizado"))

        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro ao tentar disponibilizar completo Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    @action("publish", _("Publicar"), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_article_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_("Artigo(s) publicado com sucesso!!"))

        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro tentando publicar o(s) número(s)!!. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    def unpublish_articles(self, ids, reason):
        try:
            controllers.set_article_is_public_bulk(ids, False, reason)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_("Artigo(s) despublicado com sucesso!!"))
        except Exception as ex:
            flash(
                _(
                    "Ocorreu um erro tentando despublicar o(s) número(s)!!. Erro: %(ex)s",
                    ex=str(ex),
                ),
                "error",
            )

    # Veja: https://github.com/scieloorg/opac/issues/411#issuecomment-265515533
    @action(
        "unpublish_default",
        _("Despublicar por %s" % choices.UNPUBLISH_REASONS[0]),
        ACTION_UNPUBLISH_CONFIRMATION_MSG,
    )
    def unpublish_default(self, ids):
        self.unpublish_articles(ids, choices.UNPUBLISH_REASONS[0])


class PagesAdminView(OpacBaseAdminView):
    can_create = True
    can_edit = True
    edit_modal = False
    can_delete = True
    create_modal = False
    edit_modal = False
    can_view_details = True
    column_exclude_list = ("_id",)
    column_searchable_list = ("name", "description")

    column_exclude_list = [
        "_id",
        "content",
    ]

    column_labels = dict(
        name=__("Nome"),
        language=__("Idioma"),
        content=__("Conteúdo"),
        journal=__("Periódico"),
        description=__("Descrição"),
        created_at=__("Data de Criação"),
        updated_at=__("Data de Atualização"),
    )

    column_filters = [
        "name",
        "language",
        "journal",
        "is_draft",
        "created_at",
        "updated_at",
    ]

    column_searchable_list = [
        "name",
        "description",
        "content",
    ]

    create_template = "admin/pages/add.html"
    edit_template = "admin/pages/edit.html"

    form_overrides = dict(
        language=Select2Field, journal=Select2Field, content=CKEditorField
    )

    form_args = dict(
        language=dict(choices=choices.LANGUAGES_CHOICES),
        journal=dict(
            choices=[("", "------")]
            + [(journal.acronym, journal.title) for journal in Journal.objects.all()]
        ),
    )

    form_excluded_columns = ("created_at", "updated_at")

    @admin.expose("/ajx/", methods=("GET", "POST"))
    def save_ajax_view(self):
        """
        View to save page (time to time).
        """
        try:
            p = Pages(id=request.args.get("id"), **request.form)
            p.save()
        except Exception as ex:
            return jsonify({"saved": False, "error": ex})
        else:
            return jsonify({"saved": True})

    @admin.expose("/preview/", methods=("GET",))
    def preview(self):
        """
        View to preview the page about the journal.
        """

        # page id
        id = request.args.get("id")

        page = controllers.get_page_by_id(id)

        journal = controllers.get_journal_by_acron(page.journal)

        latest_issue = fix_journal_last_issue(journal)

        if latest_issue:
            latest_issue_legend = descriptive_short_format(
                title=journal.title,
                short_title=journal.short_title,
                pubdate=str(latest_issue.year),
                volume=latest_issue.volume,
                number=latest_issue.number,
                suppl=latest_issue.suppl_text,
                language=page.language[:2].lower(),
            )
        else:
            latest_issue_legend = None

        context = {
            "journal": journal,
            "latest_issue_legend": latest_issue_legend,
            "last_issue": latest_issue,
            "journal_study_areas": [
                choices.STUDY_AREAS.get(study_area.upper())
                for study_area in journal.study_areas
            ],
        }

        if page:
            context["content"] = page.content
            if page.updated_at:
                context["page_updated_at"] = page.updated_at

        return render_template("journal/about.html", **context)

    def _content_formatter(self, context, model, name):
        return Markup(model.content)

    def _created_at_formatter(self, context, model, name):
        if model.created_at:
            return model.created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""

    def _updated_at_formatter(self, context, model, name):
        if model.updated_at:
            return model.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""

    column_formatters = dict(
        content=_content_formatter,
        created_at=_created_at_formatter,
        updated_at=_updated_at_formatter,
    )

    def on_model_delete(self, model):
        # AUDITORIA: daqui para baixo tem que modularizar para que fique generico:
        audit_payload = {
            "_id": str(uuid4().hex),
            "object_class_name": "Page",
            "object_pk": model._id,
            "action": "DEL",
            "description": "Foi apagado o registro do modelo: Page: (id: %s)"
            % model._id,
        }

        if login.current_user.is_authenticated:
            audit_payload["user"] = login.current_user.email

        audit_doc = AuditLogEntry(**audit_payload)
        audit_doc.save()

    def on_model_change(self, form, model, is_created):
        # é necessario definir um valor para o campo ``_id`` na criação.
        if is_created:
            model._id = str(uuid4().hex)

        # AUDITORIA: daqui para baixo tem que modularizar para que fique generico:
        audit_payload = {
            "_id": str(uuid4().hex),
            "object_class_name": "Page",
            "object_pk": model._id,
        }

        new_content = migrate_page_content(
            model.content, model.language, page_name=model.name
        )
        model.content = new_content
        form._fields["content"].data = new_content
        if login.current_user.is_authenticated:
            audit_payload["user"] = login.current_user.email

        if is_created:
            audit_payload["action"] = "ADD"
            audit_payload["description"] = (
                "Foi criado um novo registro de Page: (id: %s)" % model._id
            )
        else:
            audit_payload["action"] = "UPD"
            audit_payload["description"] = (
                "Foi atualizado o registro de Page: (id: %s)" % model._id
            )

        # get fields data:
        fields_to_audit = ["name", "language", "content", "journal", "description"]
        fields_data = {
            field: {"new_value": None, "old_value": None} for field in fields_to_audit
        }

        # percorremos os campos do MODELO (no banco) e do FORMULARIO e coletamos seus valores
        for field_name in fields_to_audit:
            if field_name in fields_to_audit:
                form_field_value = form._fields.get(field_name, None)
                # pegamos o novo valor do campo que vem no FORMULARIO
                form_field_value_data = (
                    form_field_value.data if form_field_value else "[NO DATA]"
                )
                fields_data[field_name]["new_value"] = form_field_value_data

                # pegamos o antigo valor do campo que vem do MODELO no banco
                if is_created:
                    fields_data[field_name]["old_value"] = "[NO DATA]"
                else:
                    old_model = Pages.objects.get(pk=model._id)
                    model_field_value_data = getattr(old_model, field_name, "[no data]")
                    fields_data[field_name]["old_value"] = model_field_value_data

        audit_payload["fields_data"] = fields_data
        audit_doc = AuditLogEntry(**audit_payload)
        audit_doc.save()


class PressReleaseAdminView(OpacBaseAdminView):
    can_create = False
    can_edit = False
    edit_modal = False
    can_delete = False
    create_modal = False
    edit_modal = False
    can_view_details = True
    form_excluded_columns = ("created", "updated")
    column_searchable_list = (
        "title",
        "content",
        "doi",
    )

    column_exclude_list = [
        "_id",
        "content",
        "created",
        "updated",
    ]

    form_overrides = dict(language=Select2Field, content=CKEditorField)

    form_ajax_refs = {
        "journal": CustomQueryAjaxModelLoader(
            name="journal",
            model=Journal,
            fields=["title", "acronym", "scielo_issn", "print_issn", "eletronic_issn"],
        ),
        "issue": CustomQueryAjaxModelLoader(
            name="issue", model=Issue, fields=["label", "pid", "journal"]
        ),
        "article": CustomQueryAjaxModelLoader(
            name="article", model=Article, fields=["title", "doi", "pid"]
        ),
    }

    form_args = dict(
        language=dict(choices=choices.LANGUAGES_CHOICES),
    )


class AuditLogEntryAdminView(OpacBaseAdminView):
    can_create = False
    can_edit = False
    can_delete = False
    column_searchable_list = (
        "description",
        "user",
    )
    column_default_sort = ("created_at", True)

    column_filters = [
        "user",
        "action",
        "created_at",
        "object_class_name",
        "object_pk",
    ]
    column_exclude_list = [
        "_id",
        "content",
        "fields_data",
    ]

    def _created_at_formatter(self, context, model, name):
        if model.created_at:
            return model.created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""

    def _action_formatter(self, context, model, name):
        label = {
            "ADD": "label label-success",
            "UPD": "label label-info",
            "DEL": "label label-danger",
        }
        if model.action:
            return Markup(
                '<span class="%s">%s</span>'
                % (label[model.action], model.get_action_value)
            )
        else:
            return "?"

    def _object_pk_formatter(self, context, model, name):
        if model.object_pk and model.object_class_name in ["Page"]:
            object_url = url_for("pages.details_view") + "?id=%s" % model.object_pk
            return Markup('<a href="%s">%s</a>' % (object_url, model.object_pk))
        else:
            return model.object_pk

    def _fields_data_formatter(self, context, model, name):
        if model.fields_data:
            result_html = render_template(
                "admin/audit_log/fields_data_table.html",
                **{"row_data": model.fields_data}
            )
            return Markup(result_html)
        else:
            return ""

    column_formatters = dict(
        action=_action_formatter,
        created_at=_created_at_formatter,
        object_pk=_object_pk_formatter,
        fields_data=_fields_data_formatter,
    )

    column_labels = dict(
        user=__("Usuário"),
        action=__("Ação"),
        created_at=__("Data de Criação"),
        object_class_name=__("Modelo Auditado"),
        object_pk=__("Id Auditado"),
        description=__("Descrição"),
        fields_data=__("Dados dos campos"),
    )
