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
from docker import Client
from horizon import views
from horizon import forms
from horizon import exceptions
from horizon import tables
from django.core.urlresolvers import reverse_lazy
from horizon import workflows
from openstack_dashboard.dashboards.docker_management.containers import workflows as create_container_workflows
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from openstack_dashboard.dashboards.docker_management.containers import tables as container_tables
from openstack_dashboard.dashboards.docker_management.containers import forms as containers_forms
import re


class IndexView(tables.DataTableView):
    table_class = container_tables.ContainerTable
    template_name = 'docker_management/containers/index.html'
    page_title = _("Docker Containers")

    def get_data(self):
        db_service = docker_host_database.DataService()
        docker_container_list = []
        try:

            for host in db_service.session.query(docker_host_database.DockerHost).order_by(
                    docker_host_database.DockerHost.id):
                docker_cli = Client(base_url='tcp://' + host.host_url + ':2376')
                containers = docker_cli.containers(all=True)
                for container in containers:
                    names = container['Names']
                    container_id = container['Id']
                    state = container['State']
                    status = container['Status']
                    host_name = host.host_name
                    image = container['Image']
                    ips = []
                    ports = []
                    for network_name, network_detail in container['NetworkSettings']['Networks'].iteritems():
                        ips.append(network_name + " : " + network_detail['IPAddress'])
                    for port in container['Ports']:
                        try:
                            port_type = port['Type']
                        except KeyError:
                            port_type = ''
                        try:
                            public_port = port['PublicPort']
                        except KeyError:
                            public_port = ''
                        try:
                            private_port = port['PrivatePort']
                        except KeyError:
                            private_port = ''
                        ports.append(port_type + ":" + str(public_port) + "->" + str(private_port))
                    docker_container_list.append(
                        container_tables.ContainerData(
                            container_id, host.id, names, state, status, ips, ports, host_name, image
                        )
                    )
        except Exception:
            docker_container_list = []
            msg = _('Container list can not be retrieved. Error has been fired!')
            exceptions.handle(self.request, msg)
        return docker_container_list


class DetailView(views.APIView):
    # A very simple class-based view...
    template_name = 'docker_management/containers/detail.html'

    def get_data(self, request, context, *args, **kwargs):
        init_id = re.split(r"[:]", self.kwargs['container_id'])
        container_id = init_id[0]
        host_id = init_id[1]
        db_service = docker_host_database.DataService()
        try:

            host_url = db_service.session.query(docker_host_database.DockerHost). \
                filter_by(id=host_id).first().host_url
            docker_cli = Client(base_url='tcp://' + host_url + ':2376')
            container = docker_cli.containers(all=True, filters={'id': container_id})[0]
            names = container['Names']
            container_id = container['Id']
            state = container['State']
            status = container['Status']
            image = container['Image']
            ips = []
            ports = []
            for network_name, network_detail in container['NetworkSettings']['Networks'].iteritems():
                ips.append(network_name + " : " + network_detail['IPAddress'])
            for port in container['Ports']:
                ports.append(port['Type'] + ":" + str(port['PublicPort']) + "->" + str(port['PrivatePort']))
            context['container'] = ContainerDetail(
                container_id, names, state, status, ips, ports, host_url, image
            )
        except Exception:
            context['container'] = []
            msg = _('Container can not be retrieved. Error has been fired!')
            exceptions.handle(self.request, msg)
        return context


class ContainerDetail:
    def __init__(self, container_id, names, state, status, ips, ports, host_url, image):
        self.id = container_id
        self.names = names
        self.status = status
        self.state = state
        self.image = image
        self.ips = ips
        self.ports = ports
        self.host_url = host_url

#
# class CreateView(forms.ModalFormView):
#     workflow_class = create_container_workflows.CreateRunningContainer
#     form_class = containers_forms.CreateContainerForm
#     form_id = "add_docker_container"
#     modal_header = _("Add  A Container")
#     submit_label = _("Add Container")
#     submit_url = reverse_lazy('horizon:docker_management:containers:create')
#     template_name = 'docker_management/hosts/create.html'
#     success_url = reverse_lazy('horizon:docker_management:containers:index')
#     page_title = _("Add A Container")
#
#     def get_initial(self):
#         initial = {}
#         return initial


class CreateView(workflows.WorkflowView):
    workflow_class = create_container_workflows.CreateRunningContainer
    template_name = 'docker_management/containers/create.html'
    context_object_name = "workflow"
    ajax_template_name = 'docker_management/containers/create_service.html'
    # ajax_template_name = 'docker_management/networks/create.html'
