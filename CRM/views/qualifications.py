from django.shortcuts import render
from CRM.models import Qualifiacation
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    UpdateView, CreateView, DetailView, DeleteView
)
from django_filters.views import FilterView
from rules.contrib.views import PermissionRequiredMixin
from CRM.filters import QualificationsFilter
from CRM.forms import QualificationsForm


class ShowQualification(PermissionRequiredMixin, FilterView):
    model = Qualifiacation
    template_name = 'CRM/qualifications/qualifications.html'
    queryset = model.objects.all().order_by('name_qualification')
    filterset_class = QualificationsFilter
    context_object_name = 'qualifications'
    paginate_by = 25
    permission_required = 'manager'


class CreateQualifications(PermissionRequiredMixin, CreateView):
    model = Qualifiacation
    success_url = reverse_lazy('qualifications:list')
    form_class = QualificationsForm
    template_name = 'CRM/qualifications/add.html'
    permission_required = 'manager'


class DetailQualifications(PermissionRequiredMixin, DetailView):
    model = Qualifiacation
    template_name = 'CRM/qualifications/detail.html'
    context_object_name = 'qualification'
    permission_required = 'manager'


class UpdateQualifications(PermissionRequiredMixin, UpdateView):
    model = Qualifiacation
    form_class = QualificationsForm
    template_name = 'CRM/qualifications/add.html'
    permission_required = 'manager'


class DeleteQualifications(PermissionRequiredMixin, DeleteView):
    model = Qualifiacation
    template_name = 'CRM/qualifications/confirm_delete.html'
    success_url = reverse_lazy('qualifications:list')
    permission_required = 'manager'

