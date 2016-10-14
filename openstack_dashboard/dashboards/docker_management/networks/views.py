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

from horizon import exceptions
from horizon import tables
from horizon import workflows
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from openstack_dashboard.dashboards.docker_management.networks import tables as network_tables
from openstack_dashboard.dashboards.docker_management.networks.tables import DockerSubnetData
from openstack_dashboard.dashboards.docker_management.networks import workflows as network_create_workflows


class IndexView(tables.DataTableView):
    table_class = network_tables.NetworksTable
    template_name = 'docker_management/networks/index.html'
    page_title = _("Docker Networks")

    def get_data(self):
        # Add data to the context here...
        try:
            db_service = docker_host_database.DataService()
            docker_networks = []
            for host in db_service.session.query(docker_host_database.DockerHost).order_by(
                    docker_host_database.DockerHost.id):
                docker_cli = Client(base_url='tcp://' + host.host_url + ':2376')
                networks_data = docker_cli.networks()
                for network in networks_data:
                    network_id = network['Id']
                    name = network['Name']
                    driver = network['Driver']
                    scope = network['Scope']
                    host_name = host.host_name
                    subnets = []
                    for subnet in network['IPAM']['Config']:
                        subnet_address = subnet['Subnet']
                        try:
                            subnet_gateway = subnet['Gateway']
                        except KeyError:
                            subnet_gateway = 'No Gateway'
                        subnets.append(DockerSubnetData(subnet_address, subnet_gateway))
                    docker_networks.append(
                        network_tables.DockerNetworkData(
                            network_id,str(host.id), name, driver, subnets, scope, host_name
                        )
                    )
        except Exception:
            docker_networks = []
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return docker_networks


class CreateView(workflows.WorkflowView):
    workflow_class = network_create_workflows.CreateNetwork
    # ajax_template_name = 'docker_management/networks/create.html'
