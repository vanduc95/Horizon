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
from openstack_dashboard.dashboards.log_management.images import models as project_model

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'log_management/images/index.html'
    table_class = project_table.Image
    page_title = 'Image Docker'

    def get_data(self):
        context =[]
        session = project_model.create_session()
        for url, port in session.query(project_model.DockerHost.host_url, project_model.DockerHost.host_port):
            base_url = 'tcp://'+url+':'+port
            cli = Client(base_url=base_url)
            images = cli.images()
            for img in images:
                imgObj = project_table.ImageObj(img['RepoTags'],img['Size'],img['Id'],img['ParentId'],url,port)
                context.append(imgObj)
        session.close()
        return context

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        docker_host = []
        session = project_model.create_session()
        for url, port in session.query(project_model.DockerHost.host_url, project_model.DockerHost.host_port):
            host = url+':'+port
            docker_host.append(host)
        context['docker_host']=docker_host
        return context


class AddDockerHost(forms.ModalFormView):
    form_class = project_form.AddDockerHost
    modal_header = _('Add Docker Host')
    form_id ='add_docker_host'
    template_name = 'log_management/images/add.html'
    success_url= reverse_lazy('horizon:log_management:images:index')
    error_url =  reverse_lazy('horizon:log_management:images:index')
    submit_url = reverse_lazy("horizon:log_management:images:add")
    page_title = _('Add Docker Host')


class CreateImage(forms.ModalFormView):
    form_class = project_form.CreateImage
    modal_header = _('Create An Image')
    template_name = 'log_management/images/create.html'
    submit_url = reverse_lazy('horizon:log_management:images:create')
    success_url = reverse_lazy('horizon:log_management:images:index')
    page_title = _('Create An Image')
