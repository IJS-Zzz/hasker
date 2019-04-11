from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

from .forms import SingUpForm, UserEditForm
from .models import User


class SingUpView(CreateView):
    form_class = SingUpForm
    template_name = 'account/sing_up.html'
    success_url = reverse_lazy("account:login")
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


class LoginView(LoginView):
    template_name = 'account/login.html'


class LogoutView(LogoutView):
    template_name = 'account/logout.html'


class UserEditView(LoginRequiredMixin, UpdateView):
    form_class = UserEditForm
    template_name = "account/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user


class UserProfileView(DetailView):
    model = User
    template_name = "account/profile.html"
    context_object_name = "profile"
    slug_url_kwarg = "username"
    slug_field = "username"
