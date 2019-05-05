from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import User
from .widgets import ClearableImageInput


class SingUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('A user with that email address already exists.'))
        return email


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'avatar',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget = ClearableImageInput()

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance.email != email:
            if User.objects.filter(email=email).exists():
                raise ValidationError(_('A user with that email address already exists.'))
        return email
