from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView,
)
from rules.contrib.views import PermissionRequiredMixin


class CrmLoginRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return reverse('accounts:login')
        elif self.request.user.is_superuser:
            return reverse('admin:index')
        elif self.request.user.is_admin:
            return reverse('accounts:login')
        elif self.request.user.is_manager:
            return reverse('accounts:login')
        elif self.request.user.is_worker:
            return reverse('accounts:login')
        else:
            return reverse('accounts:login')
