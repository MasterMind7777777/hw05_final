from django.views.generic import CreateView
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from .forms import CreationForm, ChangeForm, PasswordReset


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    form_class = ChangeForm
    template_name = 'users/password_change_form.html'


class PasswordReset(PasswordResetView):
    form_class = PasswordReset
    template_name = 'users/password_reset_form.html'
