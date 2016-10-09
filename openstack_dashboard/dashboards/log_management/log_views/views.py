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

from horizon import tables
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.log_management.log_views import  tables as log_tables
from openstack_dashboard.dashboards.log_management.log_views.log_file.log_nova import handleFile

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'log_management/log_views/index.html'
    table_class = log_tables.LogTable
    page_title = _("Log Views")

    def get_data(self):
        project = 'NOVA'
        level = 'ALL'
        timeStart = ''
        timeEnd = ''
        context = handleFile(project,level,timeStart,timeEnd)
        return context


