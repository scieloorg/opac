# coding: utf-8

import wtforms
from flask import current_app
from flask_admin.form.upload import (
    FileUploadField,
    FileUploadInput,
    ImageUploadField,
    ImageUploadInput,
)
from webapp.utils import namegen_filename, thumbgen_filename


class RequiredBooleanField(wtforms.fields.SelectField):
    # wtforms/flask-admin has a flaw related
    # to boolean fields with required=True in the model
    # Ultimatelly false values wouldn't pass validation of the form
    # thus the workaround
    def __init__(self, *args, **kwargs):
        choices = [
            (True, "True"),
            (False, "False"),
        ]

        kwargs["choices"] = choices
        kwargs["coerce"] = lambda x: str(x) == "True"

        super(RequiredBooleanField, self).__init__(*args, **kwargs)


class MediaImageUploadInput(ImageUploadInput):
    data_template = (
        '<div class="image-thumbnail">'
        " <img %(image)s>"
        # ' <input type="checkbox" name="%(marker)s">Delete</input>'
        "</div>"
        "<input %(file)s>"
    )


class MediaFileUploadInput(FileUploadInput):
    """
    Renders a file input chooser field.
    You can customize `empty_template` and `data_template` members to customize
    look and feel.
    """

    data_template = (
        "<div>"
        " <input %(text)s>"
        # ' <input type="checkbox" name="%(marker)s">Delete</input>'
        "</div>"
        "<input %(file)s>"
    )


class MediaImageUploadField(ImageUploadField):
    widget = MediaImageUploadInput()

    def __init__(
        self,
        label=None,
        validators=None,
        base_path=None,
        relative_path=None,
        namegen=None,
        allowed_extensions=None,
        max_size=None,
        thumbgen=None,
        thumbnail_size=None,
        permission=0o666,
        url_relative_path=None,
        endpoint=None,
        **kwargs
    ):
        """
        Constructor.
        :param label:
            Display label
        :param validators:
            Validators
        :param base_path:
            Absolute path to the directory which will store files
        :param relative_path:
            Relative path from the directory. Will be prepended to the file name for uploaded files.
            Flask-Admin uses `urlparse.urljoin` to generate resulting filename, so make sure you have
            trailing slash.
        :param namegen:
            Function that will generate filename from the model and uploaded file object.
            Please note, that model is "dirty" model object, before it was committed to database.
            For example::
                import os.path as op
                def prefix_name(obj, file_data):
                    parts = op.splitext(file_data.filename)
                    return secure_filename('file-%s%s' % parts)
                class MyForm(BaseForm):
                    upload = FileUploadField('File', namegen=prefix_name)
        :param allowed_extensions:
            List of allowed extensions. If not provided, then gif, jpg, jpeg, png and tiff will be allowed.
        :param max_size:
            Tuple of (width, height, force) or None. If provided, Flask-Admin will
            resize image to the desired size.
            Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
            keep aspect ratio, otherwise will just resize to target size.
        :param thumbgen:
            Thumbnail filename generation function. All thumbnails will be saved as JPEG files,
            so there's no need to keep original file extension.
            For example::
                import os.path as op
                def thumb_name(filename):
                    name, _ = op.splitext(filename)
                    return secure_filename('%s-thumb.jpg' % name)
                class MyForm(BaseForm):
                    upload = ImageUploadField('File', thumbgen=thumb_name)
        :param thumbnail_size:
            Tuple or (width, height, force) values. If not provided, thumbnail won't be created.
            Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
            keep aspect ratio, otherwise will just resize to target size.
        :param url_relative_path:
            Relative path from the root of the static directory URL. Only gets used when generating
            preview image URLs.
            For example, your model might store just file names (`relative_path` set to `None`), but
            `base_path` is pointing to subdirectory.
        :param endpoint:
            Static endpoint for images. Used by widget to display previews. Defaults to 'static'.
        """

        if not label:
            label = "File"

        if not base_path:
            base_path = current_app.config["MEDIA_ROOT"]

        if not relative_path:
            relative_path = "images/"

        if not namegen:
            namegen = namegen_filename

        if not allowed_extensions:
            allowed_extensions = current_app.config["IMAGES_ALLOWED_EXTENSIONS"]

        thumbgen = thumbgen_filename
        thumbnail_size = (100, 100, False)

        if not endpoint:
            endpoint = "main.download_file_by_filename"

        super(MediaImageUploadField, self).__init__(
            label,
            validators,
            base_path=base_path,
            relative_path=relative_path,
            namegen=namegen,
            allowed_extensions=allowed_extensions,
            thumbgen=thumbgen,
            thumbnail_size=thumbnail_size,
            permission=permission,
            endpoint=endpoint,
            **kwargs
        )

    def _save_image(self, image, path, format="JPEG"):
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        with open(path, "wb") as fp:
            image.save(fp, format)


class MediaFileUploadField(FileUploadField):
    widget = MediaFileUploadInput()

    def __init__(
        self,
        label=None,
        validators=None,
        base_path=None,
        relative_path=None,
        namegen=None,
        allowed_extensions=None,
        permission=0o666,
        allow_overwrite=True,
        **kwargs
    ):
        """
        Constructor.
        :param label:
            Display label
        :param validators:
            Validators
        :param base_path:
            Absolute path to the directory which will store files
        :param relative_path:
            Relative path from the directory. Will be prepended to the file name for uploaded files.
            Flask-Admin uses `urlparse.urljoin` to generate resulting filename, so make sure you have
            trailing slash.
        :param namegen:
            Function that will generate filename from the model and uploaded file object.
            Please note, that model is "dirty" model object, before it was committed to database.
            For example::
                import os.path as op
                def prefix_name(obj, file_data):
                    parts = op.splitext(file_data.filename)
                    return secure_filename('file-%s%s' % parts)
                class MyForm(BaseForm):
                    upload = FileUploadField('File', namegen=prefix_name)
        :param allowed_extensions:
            List of allowed extensions. If not provided, will allow any file.
        :param allow_overwrite:
            Whether to overwrite existing files in upload directory. Defaults to `True`.
        .. versionadded:: 1.1.1
            The `allow_overwrite` parameter was added.
        """

        if not label:
            label = "File"

        if not base_path:
            base_path = current_app.config["MEDIA_ROOT"]

        if not relative_path:
            relative_path = "files/"

        if not namegen:
            namegen = namegen_filename

        if not allowed_extensions:
            allowed_extensions = current_app.config["FILES_ALLOWED_EXTENSIONS"]

        super(MediaFileUploadField, self).__init__(
            label,
            validators,
            base_path=base_path,
            relative_path=relative_path,
            namegen=namegen,
            allowed_extensions=allowed_extensions,
            permission=permission,
            **kwargs
        )
