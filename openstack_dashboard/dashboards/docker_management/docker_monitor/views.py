# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
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
