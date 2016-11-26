# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from django.utils.translation import ugettext_lazy as _
from docker import Client
from horizon import exceptions
from horizon import tabs
from openstack_dashboard.dashboards.service_management.container_service.container \
    import tables as container_tables
from openstack_dashboard.dashboards.service_management.container_service.service \
    import tables as service_tables
from openstack_dashboard.dashboards.service_management.container_service.database \
    import services as database_service

INFO_DETAIL_TEMPLATE_NAME = 'horizon/common/_detail_table.html'


class ContainerTab(tabs.TableTab):
    table_classes = (container_tables.ContainerTable,)
    name = container_tables.ContainerTable.Meta.verbose_name
    slug = container_tables.ContainerTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    def get_containers_data(self):
        container_list = []
        try:

            docker_cli = Client(base_url='tcp://' + '127.0.0.1' + ':2376')
            containers = docker_cli.containers(all=True)
            for container in containers:
                names = container['Names']
                service_name = 'not set'
                container_id = container['Id']
                state = container['State']
                status = container['Status']
                image = container['Image']
                ips = []
                ports = []
                for network_name, network_detail in\
                        container['NetworkSettings']['Networks'].iteritems():
                    ips.append(network_name + " : " +
                               network_detail['IPAddress'])
                for port in container['Ports']:
                    if 'PublicPort' in port:
                        public_port = port['PublicPort']
                    else:
                        public_port = 'not set'
                    if 'PrivatePort' in port:
                        private_port = port['PrivatePort']
                    else:
                        private_port = 'not set'
                    ports.append(
                        port['Type'] + ":" + str(public_port) + "->" +
                        str(private_port))
                container_list.append(
                    ContainerData(
                        container_id,
                        names, service_name, state,
                        status, ips, ports, image
                    )
                )
        except Exception as e:
            container_list = []
            msg = _(e.message)
            exceptions.handle(self.request, msg)
        return container_list


class ServiceTab(tabs.TableTab):
    table_classes = (service_tables.ServiceTable,)
    name = service_tables.ServiceTable.Meta.verbose_name
    slug = service_tables.ServiceTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    class ServiceData:

        def __init__(self, id, name):
            self.id = id
            self.name = name

    def get_services_data(self):
        services = []
        db_service = database_service.DatabaseService()
        for service in db_service.session.query(database_service.Service):
            services.append(ServiceTab.ServiceData(service.id,service.service_name))
        db_service.close()
        return services


class ContainerAndServiceTabs(tabs.TabGroup):
    slug = "container_and_service"
    tabs = (ContainerTab, ServiceTab)
    sticky = True


class ContainerData:

    def __init__(self, container_id, names, service_name, state, status, ips, ports, image):
        self.id = container_id
        self.names = names
        self.service_name = service_name
        self.status = status
        self.state = state
        self.image = image
        self.ips = ips
        self.ports = ports
