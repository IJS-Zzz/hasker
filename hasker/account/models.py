import os
import hashlib

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .fields import AvatarImageField


def unique_avatar_filename(instance, filename):
    file_path = settings.AVATAR_FILE_PATH
    chunk_size = 65536
    hasher = hashlib.md5()
    instance.avatar.open()
    buf = instance.avatar.read(chunk_size)
    while len(buf) > 0:
        hasher.update(buf)
        buf = instance.avatar.read(chunk_size)
    _, ext = os.path.splitext(filename)
    filename = '{}{}'.format(hasher.hexdigest(), ext)
    return os.path.join(file_path, filename)


class User(AbstractUser):
    avatar = AvatarImageField(
        _('avatar'),
        upload_to=unique_avatar_filename,
        content_types=settings.AVATAR_CONTENT_TYPES,
        max_upload_size=(settings.AVATAR_MAX_SIZE_MB * 1024 * 1024),
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return reverse('account:profile', kwargs={'username': self.username})

    def get_avatar_url(self):
        if self.avatar:
            if self.avatar.storage.exists(self.avatar.name):
                return self.avatar.url
            self.avatar.delete()
        return staticfiles_storage.url('img/avatar.png')

    @property
    def url(self):
        return self.get_absolute_url()
