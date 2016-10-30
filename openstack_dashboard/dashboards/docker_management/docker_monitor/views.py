from django.utils.translation import ugettext_lazy as _
from horizon import tabs
from openstack_dashboard.dashboards.docker_management.docker_monitor import tabs as docker_tabs


class IndexView(tabs.TabbedTableView):
    tab_group_class = docker_tabs.ContainerHostIpTabs
    template_name = 'docker_management/docker_monitor/index.html'
    page_title = _("Docker Management")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context
