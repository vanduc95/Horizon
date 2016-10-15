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
from openstack_dashboard.dashboards.log_management.images import tables as project_table
from openstack_dashboard.dashboards.log_management.images import forms as project_form
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from docker import Client
from horizon import forms

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'log_management/images/index.html'
    table_class = project_table.Image
    page_title = 'Image Docker'

    def get_data(self):
        context =[]
        cli = Client(base_url='unix://var/run/docker.sock')
        images = cli.images()
        for img in images:
            imgObj = project_table.ImageObj(img['RepoTags'],img['Size'],img['Id'],img['ParentId'])
            context.append(imgObj)
        return context

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context



class CreateImage(forms.ModalFormView):
    form_class = project_form.CreateImage
    modal_header = _('Create An Image')
    template_name = 'log_management/images/create.html'
    submit_url = reverse_lazy('horizon:log_management:images:index')
    page_title = _('Create An Image')
