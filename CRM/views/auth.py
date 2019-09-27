from django.shortcuts import render
from CRM.models import Worker
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordContextMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView, CreateView, FormView
)
from rules.contrib.views import PermissionRequiredMixin
from CRM.forms import ProfileAdminForm, UserForm


class CrmLoginRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return reverse('accounts:login')
        elif self.request.user.is_superuser:
            return reverse('admin:index')
        elif not self.request.user.is_first_login:
            return reverse('accounts:password-change-first')
        elif self.request.user.is_admin or self.request.user.is_manager or self.request.user.is_worker:
            return reverse('accounts:profile')
        else:
            return reverse('accounts:login')


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


class CreateUser(PermissionRequiredMixin, FormView):
    model = Worker
    success_url = reverse_lazy('accounts:password-see')
    form_class = UserForm
    template_name = 'CRM/user/form.html'
    permission_required = 'add_user'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        username = self.request.user.generate_username(request.POST['first_name'],
                                                       request.POST['last_name'], request.POST['patronymic'])
        password = Worker.objects.make_random_password()
        if self.request.user.is_admin:
            user = Worker.objects.create_user(username=username, password=password, is_manager_user=True,
                                              status_id=request.POST['status'],
                                              qualifiacation_id=request.POST['qualifiacation'],
                                              first_name=request.POST['first_name'],
                                              last_name=request.POST['last_name'],
                                              patronymic=request.POST['patronymic'])
        elif not self.request.user.is_manager:
            user = Worker.objects.create_user(username=username, password=password, is_worker_user=True,
                                              status_id=request.POST['status'],
                                              qualifiacation_id=request.POST['qualifiacation'],
                                              first_name=request.POST['first_name'],
                                              last_name=request.POST['last_name'],
                                              patronymic=request.POST['patronymic']
                                              )
        user.save()
        return render(request, 'CRM/user/password.html', context={'password': password})


class PasswordSee(PermissionRequiredMixin, TemplateView):
    success_url = reverse_lazy('accounts:profile')
    template_name = 'CRM/user/password.html'
    title = 'Password See'
    permission_required = 'add_user'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


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
