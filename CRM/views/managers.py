from CRM.models import Worker
from rules.contrib.views import PermissionRequiredMixin
from django_filters.views import FilterView
from CRM.models import Worker


class ShowManagers(PermissionRequiredMixin,FilterView):
    model=Worker
    queryset = Worker.objects.filter(is_manager_user=True)
    template_name = 'CRM/manager/managers.html'
    context_object_name = 'managers'
    paginate_by = 25
    permission_required = 'admin'
