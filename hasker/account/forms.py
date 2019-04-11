from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User
from .widgets import ClearableImageInput


class SingUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar',)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'avatar',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget = ClearableImageInput()