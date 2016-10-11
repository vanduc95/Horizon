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

from horizon import exceptions
from horizon import tables
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from openstack_dashboard.dashboards.docker_management.containers import tables as container_tables
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
                        ports.append(port['Type'] + ":" + str(port['PublicPort']) + "->" + str(port['PrivatePort']))
                    docker_container_list.append(
                        container_tables.ContainerData(
                            container_id,host.id, names, state, status, ips, ports, host_name, image
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
        init_id = re.split(r"[:]",self.kwargs['container_id'])
        container_id = init_id[0]
        host_id = init_id[1]
        db_service = docker_host_database.DataService()
        try:

            host_url = db_service.session.query(docker_host_database.DockerHost).\
                filter_by(id=host_id).first().host_url
            docker_cli = Client(base_url='tcp://' + host_url + ':2376')
            container = docker_cli.containers(all=True,filters={'id':container_id})[0]
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
                container_id,names,state,status,ips,ports,host_url,image
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
