from django.shortcuts import render
from CRM.models import Worker, Time
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordContextMixin, LogoutView
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView, CreateView, FormView
)
from rules.contrib.views import PermissionRequiredMixin
from CRM.forms import ProfileAdminForm, UserForm
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger


class CrmLoginRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return reverse('accounts:login')
        elif self.request.user.is_superuser:
            return reverse('admin:index')
        elif not self.request.user.is_first_login:
            self.request.user.update_time_arrival()
            self.request.user.update_online_status()
            return reverse('accounts:password-change-first')
        elif self.request.user.is_admin or self.request.user.is_manager or self.request.user.is_worker:
            self.request.user.update_online_status()
            return reverse('accounts:profile')
        else:
            return reverse('accounts:login')


class CrmLogoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        self.request.user.update_offline_status()
        self.request.user.update_time_leaving()
        return super().dispatch(request, *args, **kwargs)


class PasswordChangeFirsView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('accounts:password-change-done')
    template_name = 'CRM/auth/password-change.html'


class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('accounts:profile')
    template_name = 'CRM/auth/password-change.html'


class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    success_url = reverse_lazy('accounts:profile')
    template_name = 'CRM/auth/password_change_done.html'
    title = 'Password change successful'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.request.user.get_update_first_user_login()
        return self.render_to_response(context)


class ProfileView(PermissionRequiredMixin, UpdateView):
    template_name = 'CRM/auth/profile.html'
    success_url = reverse_lazy('accounts:profile')
    permission_required = 'profile'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        list_exam = Time.objects.filter(worker_id=self.request.user.id).order_by('-pk')
        paginator = Paginator(list_exam, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            file_exams = paginator.page(page)
        except PageNotAnInteger:
            file_exams = paginator.page(1)
        except EmptyPage:
            file_exams = paginator.page(paginator.num_pages)

        context['times'] = file_exams
        return context

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
