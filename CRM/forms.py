from typing import Tuple, Optional
from django import forms
from django.contrib.auth import get_user_model
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from betterforms.multiform import MultiModelForm

from .models import (Qualifiacation)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('qualifiacation', 'status')
        widgets = {
            'qualifiacation': forms.Select(attrs={"class": "form-control"}),
        }


class QualificationsForm(forms.ModelForm):
    class Meta:
        model = Qualifiacation
        fields = ('name_qualification', 'money_index')


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('last_name', 'first_name',  'patronymic', 'qualifiacation')
        widgets = {
            'last_name': forms.TextInput(attrs={"class": "form-control"}),
            'first_name': forms.TextInput(attrs={"class": "form-control"}),
            'patronymic': forms.TextInput(attrs={"class": "form-control"}),
            'qualifiacation': forms.Select(attrs={"class": "form-control"}),
        }


class ProfileUserForm(forms.ModelForm):
    fullname = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(attrs={'data-name-edit': True})
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'patronymic', 'email')
        widgets = {
            'last_name': forms.HiddenInput(),
            'first_name': forms.HiddenInput(),
            'patronymic': forms.HiddenInput(),
            'email': forms.TextInput(attrs={"class": "form-control", "placeholder": "example@email.com"}),
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        instance = kwargs.get('instance', None)

        if instance:
            if initial is None:
                initial = {}
            initial['fullname'] = ''.join([str(instance.last_name), ' ', str(instance.first_name), ' ', str(instance.patronymic)])

        super(ProfileUserForm, self).__init__(*args, initial=initial, **kwargs)


class ManagerForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('phone_number',)
        widgets = {
            'phone_number': forms.TextInput(attrs={"class": "form-control", "placeholder": "Номер телефона"}),
            }


class ProfileAdminForm(MultiModelForm):
    form_classes = {
        'user': ProfileUserForm,
        'detail': ManagerForm
    }
