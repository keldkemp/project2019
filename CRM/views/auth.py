from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView,
)
from rules.contrib.views import PermissionRequiredMixin
from CRM.forms import ProfileAdminForm


class CrmLoginRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return reverse('accounts:login')
        elif self.request.user.is_superuser:
            return reverse('admin:index')
        elif not self.request.user.is_first_login:
            self.request.user.get_update_first_user_login()
            return reverse('accounts:password-change')
        elif self.request.user.is_admin or self.request.user.is_manager or self.request.user.is_worker:
            return reverse('accounts:profile')
        else:
            return reverse('accounts:login')


class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('accounts:profile')
    template_name = 'CRM/auth/password-change.html'


class ProfileView(PermissionRequiredMixin, UpdateView):
    template_name = 'CRM/auth/profile.html'
    success_url = reverse_lazy('accounts:profile')
    permission_required = 'profile'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_class(self):
        if self.request.user.is_admin or self.request.user.is_manager or self.request.user.is_worker:
            return ProfileAdminForm
        else:
            return reverse('accounts:login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(instance={
            'user': self.object,
            'detail':
                self.object
        })
        return kwargs
