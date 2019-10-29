from django_filters.views import FilterView
from django.shortcuts import render
from CRM.models import Worker, Time
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView, CreateView, FormView,
    DetailView, DeleteView)
from rules.contrib.views import PermissionRequiredMixin
from CRM.forms import UserForm, UserUpdateForm
from CRM.filters import UsersFilter
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger


class ShowUsers(PermissionRequiredMixin, FilterView):
    model = Worker
    queryset = model.objects.filter(is_superuser=False).order_by('status_id', 'last_name')
    filterset_class = UsersFilter
    template_name = 'CRM/users/users.html'
    context_object_name = 'users'
    paginate_by = 25
    permission_required = 'users_list'

    def get_permission_object(self):
        self.request.user


class DeleteUsers(PermissionRequiredMixin, DeleteView):
    model = Worker
    template_name = 'CRM/users/confirm_delete.html'
    success_url = reverse_lazy('users:list')
    permission_required = 'delete_user'

    def get_permission_object(self):
        self.request.user


class DetailUsers (PermissionRequiredMixin, DetailView):
    model = Worker
    template_name = 'CRM/users/detail.html'
    context_object_name = 'user_detail'
    permission_required = 'users_list'
    paginate_by = 7

    def get_permission_object(self):
        self.request.user

    def get_context_data(self, **kwargs):
        context = super(DetailUsers, self).get_context_data(**kwargs)
        list_exam = Time.objects.filter(worker_id=context['user_detail'].id).order_by('-pk')
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


class UpdateUsers(PermissionRequiredMixin, UpdateView):
    model = Worker
    form_class = UserUpdateForm
    template_name = 'CRM/users/update.html'
    permission_required = 'manager'
    context_object_name = 'user_detail'

    def get_permission_object(self):
        self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            if request.POST['send_to_mission'] == '3':
                self.object.update_command_status()
                self.object.create_send_to_mission(request.POST['start_mission'], request.POST['end_mission'])
                return super().post(request, *args, **kwargs)
        except:
            return super().post(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)


class CreateUser(PermissionRequiredMixin, FormView):
    model = Worker
    success_url = reverse_lazy('users:add')
    form_class = UserForm
    template_name = 'CRM/users/add.html'
    permission_required = 'add_user'

    def get_permission_object(self):
        self.request.user

    def post(self, request, *args, **kwargs):
        username = self.request.user.generate_username(request.POST['first_name'],
                                                       request.POST['last_name'], request.POST['patronymic'])
        password = Worker.objects.make_random_password()
        if self.request.user.is_admin:
            user = Worker.objects.create_user(username=username, password=password, is_manager_user=True,
                                              status_id=2,
                                              qualifiacation_id=request.POST['qualifiacation'],
                                              first_name=request.POST['first_name'],
                                              last_name=request.POST['last_name'],
                                              patronymic=request.POST['patronymic'])
        elif self.request.user.is_manager:
            user = Worker.objects.create_user(username=username, password=password, is_worker_user=True,
                                              status_id=2,
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

    def get_permission_object(self):
        self.request.user

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

