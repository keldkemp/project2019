from CRM.models import Worker
from rules.contrib.views import PermissionRequiredMixin
from django_filters.views import FilterView
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, FormView, UpdateView,
)
from CRM.filters import WorkerFilter
from CRM.forms import QualificationForm
from CRM.forms import Qualification2Form
from CRM.forms import Qualification3Form


class ShowQualifiacation(PermissionRequiredMixin, FilterView):
    model = Worker
    filterset_class = WorkerFilter
    queryset = model.objects.filter(is_manager_user=True)
    template_name = 'CRM/qualifiacation/qualifications.html'
    context_object_name = 'qualifiacation'
    paginate_by = 25
    permission_required = 'manager'


class EditQualifiacation(PermissionRequiredMixin, FormView):
    model = Worker
    success_url = reverse_lazy('qualifiacation:edit')
    form_class = QualificationForm
    template_name = 'CRM/qualifiacation/edit.html'
    permission_required = 'manager'


class CreateQualifiacation(PermissionRequiredMixin, FormView):
    model = Worker
    success_url = reverse_lazy('qualifiacation:create')
    form_class = Qualification2Form
    template_name = 'CRM/qualifiacation/create.html'
    permission_required = 'manager'


class DeleteQualifiacation(PermissionRequiredMixin, FormView):
    model = Worker
    success_url = reverse_lazy('qualifiacation:delete')
    form_class = Qualification3Form
    template_name = 'CRM/qualifiacation/delete.html'
    permission_required = 'qualifiacation_delete'

