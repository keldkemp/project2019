from rules.contrib.views import PermissionRequiredMixin
from django_filters.views import FilterView
from CRM.models import Worker


class ShowUsers(PermissionRequiredMixin, FilterView):
    model = Worker
    queryset = model.objects.filter(is_superuser=False)
    template_name = 'CRM/users/users.html'
    context_object_name = 'users'
    paginate_by = 25
    permission_required = 'admin'
