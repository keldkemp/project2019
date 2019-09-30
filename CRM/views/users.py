from django_filters.views import FilterView
from django.shortcuts import render
from CRM.models import Worker
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView, CreateView, FormView
)
from rules.contrib.views import PermissionRequiredMixin
from CRM.forms import UserForm


class ShowUsers(PermissionRequiredMixin, FilterView):
    model = Worker
    queryset = model.objects.filter(is_superuser=False)
    template_name = 'CRM/users/users.html'
    context_object_name = 'users'
    paginate_by = 25
    permission_required = 'users_list'

    def get_object(self, queryset=None):
        return self.request.user


class CreateUser(PermissionRequiredMixin, FormView):
    model = Worker
    success_url = reverse_lazy('users:add')
    form_class = UserForm
    template_name = 'CRM/users/add.html'
    permission_required = 'add_user'

    def get_object(self, queryset=None):
        return self.request.user

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
        elif self.request.user.is_manager:
            user = Worker.objects.create_user(username=username, password=password, is_worker_user=True,
                                              status_id=request.POST['status'],
                                              qualifiacation_id=request.POST['qualifiacation'],
                                              first_name=request.POST['first_name'],
                                              last_name=request.POST['last_name'],
                                              patronymic=request.POST['patronymic']
                                              )
        user.save()
        return render(request, 'CRM/users/password.html', context={'password': password,
                                                                   'username': username})


class PasswordSee(PermissionRequiredMixin, TemplateView):
    success_url = reverse_lazy('accounts:profile')
    template_name = 'CRM/users/password.html'
    title = 'Password See'
    permission_required = 'add_user'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

