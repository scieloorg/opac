from mongoengine import *
# from lxml import etree
# import packtools
CSS = "/static/css/style_article_html.css"


class DCollection(EmbeddedDocument):
    acronym = StringField(max_length=50, required=True, unique=True)
    name = StringField(max_length=100, required=True, unique_with='acronym')

    meta = {
        'collection': 'collection'
    }


class DUseLicense(EmbeddedDocument):
    license_code = StringField(required=True)
    reference_url = StringField()
    disclaimer = StringField()

    meta = {
        'collection': 'use_license'
    }


class DTimeline(EmbeddedDocument):
    since = DateTimeField()
    reason = StringField()
    status = StringField()

    meta = {
        'collection': 'timeline'
    }


class DSocialNetwork(EmbeddedDocument):
    account = StringField()
    network = StringField()

    meta = {
        'collection': 'social_network'
    }


class DOtherTitle(EmbeddedDocument):
    title = StringField()
    category = StringField()

    meta = {
        'collection': 'other_title'
    }


class DMission(EmbeddedDocument):
    language = StringField()
    description = StringField()

    meta = {
        'collection': 'mission'
    }


class DLastIssue(EmbeddedDocument):
    volume = StringField()
    number = StringField()
    year = IntField()
    label = StringField()
    start_month = IntField()
    end_month = IntField()
    sections = ListField()
    cover_url = StringField()
    iid = StringField()
    bibliographic_legend = StringField()

    meta = {
        'collection': 'last_issue'
    }


class DSubject(EmbeddedDocument):
    name = StringField()
    language = StringField()

    meta = {
        'collection': 'subjects'
    }


class DSection(EmbeddedDocument):
    order = IntField()
    subjects = EmbeddedDocumentListField(DSubject)

    meta = {
        'collection': 'sections'
    }


class DJournal(Document):
    _id = StringField(max_length=32, primary_key=True, required=True, unique=True)
    jid = StringField(max_length=32, required=True, unique=True, )
    collections = EmbeddedDocumentListField(DCollection)
    use_licenses = EmbeddedDocumentField(DUseLicense)
    timeline = EmbeddedDocumentListField(DTimeline)
    national_code = StringField()
    subject_categories = ListField()
    study_areas = ListField()
    social_networks = EmbeddedDocumentListField(DSocialNetwork)
    title = StringField()
    title_iso = StringField()
    short_title = StringField()
    created = DateTimeField()
    updated = DateTimeField()
    acronym = StringField()
    scielo_issn = StringField()
    print_issn = StringField()
    eletronic_issn = StringField()
    subject_descriptors = ListField()
    init_year = StringField()
    init_vol = StringField()
    init_num = StringField()
    final_num = StringField()
    final_vol = StringField()
    final_year = StringField()
    copyrighter = StringField()
    online_submission_url = StringField()
    cover_url = StringField()
    logo_url = StringField()
    previous_journal_id = IntField()
    other_titles = EmbeddedDocumentListField(DOtherTitle)
    publisher_name = StringField()
    publisher_country = StringField()
    publisher_state = StringField()
    publisher_city = StringField()
    publisher_address = StringField()
    publisher_telephone = StringField()
    current_status = StringField()

    mission = EmbeddedDocumentListField(DMission)
    index_at = ListField()
    sponsors = ListField()
    issue_count = IntField()
    last_issue = EmbeddedDocumentField(DLastIssue)

    meta = {
        'collection': 'journal'
    }


class DIssue(Document):

    _id = StringField(max_length=32, primary_key=True, required=True, unique=True)
    iid = StringField(max_length=32, required=True, unique=True)
    journal_jid = ReferenceField(DJournal, reverse_delete_rule=CASCADE)

    sections = EmbeddedDocumentListField(DSection)
    use_licenses = EmbeddedDocumentField(DUseLicense)

    cover_url = StringField()

    volume = StringField()
    number = StringField()
    created = DateTimeField()
    updated = DateTimeField()

    type = StringField()
    suppl_text = StringField()
    spe_text = StringField()
    start_month = IntField()
    end_month = IntField()
    year = IntField()
    label = StringField()
    order = IntField()
    bibliographic_legend = StringField()

    meta = {
        'collection': 'issue'
    }


class DArticleHTML(EmbeddedDocument):
    language = StringField()
    source = StringField()

    meta = {
        'collection': 'article_html'
    }


class DArticle(Document):
    _id = StringField(max_length=32, primary_key=True, required=True, unique=True)
    aid = StringField(max_length=32, required=True, unique=True)

    issue_iid = ReferenceField(DIssue, reverse_delete_rule=CASCADE)
    journal_jid = ReferenceField(DJournal, reverse_delete_rule=CASCADE)

    title = StringField()
    section = StringField()
    is_aop = BooleanField()
    created = DateTimeField()
    updated = DateTimeField()
    htmls = EmbeddedDocumentListField(DArticleHTML)

    domain_key = StringField()
    # journal = Nested(properties={"title": String(index="not_analyzed"),
    #                              "publisher_name": String(index="not_analyzed"),
    #                              "scielo_issn": String(index="not_analyzed"),
    #                              "print_issn": String(index="not_analyzed"),
    #                              "eletronic_issn": String(index="not_analyzed"),
    #                              "study_areas": String(index="not_analyzed")})
    # issue = Nested(properties={"year": String(index="not_analyzed"),
    #                            "volume": String(index="not_analyzed"),
    #                            "number": String(index="not_analyzed")})
    meta = {
        'collection': 'article'
    }


def get_section_titles(section):
    """
    Get all title for a section
    """

    titles = []
    for section in section.all():
        for title in section.titles.all():
            titles.append(title.title)

    return titles


def journal_to_djournal(model_instance):
    journal_collections = []
    for collection in model_instance.collections.all():
        journal_collections.append({
            'acronym': collection.acronym,
            'name': collection.name,
        })

    journal_use_licenses = None
    if model_instance.use_license:
        journal_use_licenses = {
            'license_code': model_instance.use_license.license_code,
            'reference_url': model_instance.use_license.reference_url,
            'disclaimer': model_instance.use_license.disclaimer
        }

    journal_timeline = []
    for status in model_instance.statuses.all().order_by('-since'):
        journal_timeline.append({
            'since': status.since,
            'reason': status.reason,
            'status': status.status
        })

    journal_subject_categories = [sc.term for sc in model_instance.subject_categories.all()]

    journal_study_areas = [sa.study_area for sa in model_instance.study_areas.all()]

    journal_social_networks = []
    if model_instance.twitter_user:
        journal_social_networks = [{
            'network': 'twitter',
            'account': journal.twitter_user,
        }]
    journal_cover_url = None
    if model_instance.cover:
        journal_cover_url = model_instance.cover.url

    journal_logo_url = None
    if model_instance.logo:
        journal_logo_url = model_instance.logo.url

    journal_previous_id = None
    if model_instance.previous_title:
        journal_previous_id = model_instance.previous_title.id

    journal_other_titles = []
    for title in model_instance.other_titles.all():
        journal_other_titles.append({
            'title': title.title,
            'category': title.category,
        })

    journal_current_status = None
    if model_instance.statuses.all():
        journal_current_status = model_instance.statuses.all().order_by('-since')[0].status

    journal_missions = []
    for mission in model_instance.missions.all():
        journal_missions.append({
            'language': mission.language.iso_code,
            'description': mission.description,
        })

    list_of_indexes = []
    if model_instance.is_indexed_scie:
        list_of_indexes.append('SCIE')
    if model_instance.is_indexed_ssci:
        list_of_indexes.append('SSCI')
    if model_instance.is_indexed_aehci:
        list_of_indexes.append('A&HCI')

    list_of_sponsor = []
    if model_instance.sponsor.all():
        for sponsor in model_instance.sponsor.all():
            list_of_sponsor.append(sponsor.name)

    issue = model_instance.get_last_issue()

    if issue:

        last_issue = {'volume': issue.volume,
                      'number': issue.number,
                      'year': issue.publication_year,
                      'start_month': issue.publication_start_month,
                      'end_month': issue.publication_end_month,
                      'label': issue.label,
                      'sections': get_section_titles(issue.section),
                      'iid': issue.iid,
                      'cover_url': issue.conver.path if issue.cover else None,
                      'bibliographic_legend': issue.bibliographic_legend}
    else:
        last_issue = None

    issue_count = model_instance.issue_set.all().count()

    result = {
        '_id': model_instance.jid,
        'jid': model_instance.jid,
        'collections': journal_collections,
        'use_licenses': journal_use_licenses,
        'timeline': journal_timeline,
        'national_code': model_instance.national_code,
        'subject_categories': journal_subject_categories,
        'study_areas': journal_study_areas,
        'social_networks': journal_social_networks,
        'title': model_instance.title,
        'title_iso': model_instance.title_iso,
        'short_title': model_instance.short_title,
        'created': model_instance.created,
        'updated': model_instance.updated,
        'acronym': model_instance.acronym,
        'scielo_issn': model_instance.scielo_issn,
        'print_issn': model_instance.print_issn,
        'eletronic_issn': model_instance.eletronic_issn,
        'subject_descriptors': model_instance.subject_descriptors.split('\n'),
        'init_year': model_instance.init_year,
        'init_vol': model_instance.init_vol,
        'init_num': model_instance.init_num,
        'final_num': model_instance.final_num,
        'final_vol': model_instance.final_vol,
        'final_year': model_instance.final_year,
        'copyrighter': model_instance.copyrighter,
        'online_submission_url': model_instance.url_online_submission,
        'cover_url': journal_cover_url,
        'logo_url': journal_logo_url,
        'previous_journal_id': journal_previous_id,
        'other_titles': journal_other_titles,
        'publisher_name': model_instance.publisher_name,
        'publisher_country': model_instance.publisher_country,
        'publisher_state': model_instance.publisher_state,
        'publisher_city': model_instance.publication_city,
        'publisher_address': None,  # TODO: FIX it!
        'publisher_telephone': None,  # TODO: FIX it!
        'current_status': journal_current_status,
        'mission': journal_missions,
        'index_at': list_of_indexes,
        'sponsors': list_of_sponsor,
        'last_issue': last_issue,
        'issue_count': issue_count
    }
    return result


def issue_to_dissue(model_instance):
    issue_sections = []
    for section in model_instance.section.all():
        subjects = []
        for subject in section.titles.all():
            subjects.append({
                "name": subject.title,
                "language": subject.language.iso_code,
            })

        issue_sections.append({
            # "order": section.order, FIX
            "subjects": subjects
        })

    issue_use_licenses = None
    if model_instance.use_license:
        issue_use_licenses = {
            "license_code": model_instance.use_license.license_code,
            "reference_url": model_instance.use_license.reference_url,
            "disclaimer": model_instance.use_license.disclaimer
        }

    issue_cover_url = None
    if model_instance.cover:
        issue_cover_url = model_instance.cover.url

    if model_instance.journal:
        journal_jid = model_instance.journal.jid
    else:
        journal_jid = None

    result = {
        "_id": model_instance.iid,
        "iid": model_instance.iid,
        "journal_jid": journal_jid,
        "sections": issue_sections,
        "type": model_instance.type,
        "suppl_text": model_instance.suppl_text,
        "spe_text": model_instance.spe_text,
        "volume": model_instance.volume,
        "number": model_instance.number,
        "created": model_instance.created,
        "updated": model_instance.updated,
        "start_month": model_instance.publication_start_month,
        "end_month": model_instance.publication_end_month,
        "year": model_instance.publication_year,
        "use_licenses": issue_use_licenses,
        "cover_url": issue_cover_url,
        "label": model_instance.label,
        "order": model_instance.order,
        "bibliographic_legend": model_instance.bibliographic_legend,
    }
    return result


def article_to_darticle(model_instance):

    htmls = []
    if model_instance.xml:
        try:
            for lang, output in packtools.HTMLGenerator(model_instance.xml.root_etree, valid_only=False, css=CSS):
                htmls.append({"language": lang, "source": etree.tostring(output, encoding="utf-8", method="html", doctype=u"<!DOCTYPE html>")})
        except Exception as e:
            print "Article aid: %s, sem html, Error: %s" % (model_instance.aid, e.message)

    if model_instance.issue:
        issue_iid = model_instance.issue.iid
    else:
        issue_iid = None

    if model_instance.journal:
        journal_jid = model_instance.journal.jid
    else:
        journal_jid = None

    journal_study_areas = [sa.study_area for sa in model_instance.journal.study_areas.all()]

    # journal = {
    #         "title": model_instance.journal.title,
    #         "publisher_name": model_instance.journal.publisher_name,
    #         "scielo_issn": model_instance.journal.scielo_issn,
    #         "print_issn": model_instance.journal.print_issn,
    #         "eletronic_issn": model_instance.journal.eletronic_issn,
    #         "study_areas": journal_study_areas
    #         }

    # issue = {
    #     "year": model_instance.issue.publication_year,
    #     "volume": model_instance.issue.volume,
    #     "number": model_instance.issue.number
    # }

    result = {
        "_id": model_instance.aid,
        "aid": model_instance.aid,
        "is_aop": model_instance.is_aop,
        "issue_iid": issue_iid,
        "journal_jid": journal_jid,
        "created": model_instance.created_at,
        "updated": model_instance.updated_at,
        "title": model_instance.get_value(model_instance.XPaths.ARTICLE_TITLE),
        "section": model_instance.get_value(model_instance.XPaths.HEAD_SUBJECT),
        "htmls": htmls,
        "domain_key": model_instance.domain_key,
        # "journal": journal,
        # "issue": issue
    }
    return result
