from django.core.files.uploadedfile import UploadedFile
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


class AvatarImageField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types.
            Example: ['image/png', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            1MB - 1048576
            5MB - 5242880
            10MB - 10485760
    """

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types') if 'content_types' in kwargs else []
        self.max_upload_size = kwargs.pop('max_upload_size') if 'max_upload_size' in kwargs else 0
        self._old_file = None
        super().__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        if data is not None:
            file = getattr(instance, self.attname)
            if file != data:
                self._old_file = file
        super().save_form_data(instance, data)

    def pre_save(self, model_instance, add):
        file = super().pre_save(model_instance, add)
        if self._old_file and self._old_file != file:
            self._old_file.delete(save=False)
        return file

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        file = data.file

        if isinstance(file, UploadedFile):
            content_type = file.content_type
            if content_type in self.content_types:
                if file.size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under {}. Current filesize {}').format(
                        filesizeformat(self.max_upload_size), filesizeformat(file.size))
                    )
            else:
                raise forms.ValidationError(_('Filetype not supported'))

        return data
