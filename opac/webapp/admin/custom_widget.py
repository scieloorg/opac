# coding: utf-8
from wtforms.fields import TextAreaField
from wtforms.widgets import TextArea


class CKEditorWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " ckeditor"
        else:
            kwargs.setdefault("class", "ckeditor")
        return super(CKEditorWidget, self).__call__(field, **kwargs)


class CKEditorField(TextAreaField):
    widget = CKEditorWidget()
