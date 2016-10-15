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
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from openstack_dashboard.dashboards.docker_management.docker_monitor.docker_containers \
    import tables as docker_container_tables
from openstack_dashboard.dashboards.docker_management.docker_monitor.docker_hosts \
    import tables as docker_host_tables

INFO_DETAIL_TEMPLATE_NAME = 'horizon/common/_detail_table.html'


class ContainerTab(tabs.TableTab):
    table_classes = (docker_container_tables.ContainerTable,)
    name = docker_container_tables.ContainerTable.Meta.verbose_name
    slug = docker_container_tables.ContainerTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    def get_containers_data(self):
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
                        docker_container_tables.ContainerData(
                            container_id, names, state, status, ips, ports, host_name, image
                        )
                    )
        except Exception:
            docker_container_list = []
            msg = _('Container list can not be retrieved. Error has been fired!')
            exceptions.handle(self.request, msg)
        return docker_container_list


class HostTab(tabs.TableTab):
    table_classes = (docker_host_tables.HostTable,)
    name = docker_host_tables.HostTable.Meta.verbose_name
    slug = docker_host_tables.HostTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    class DockerHostData:
        def __init__(self, id, name, host_ip):
            self.id = id
            self.name = name
            self.host_ip = host_ip

    def get_docker_hosts_data(self):
        db_service = docker_host_database.DataService()
        docker_host_list = []
        for instance in db_service.session.query(docker_host_database.DockerHost).order_by(
                docker_host_database.DockerHost.id):
            docker_host_list.append(HostTab.DockerHostData(instance.id, instance.host_name, instance.host_url))
        return docker_host_list


class ContainerHostIpTabs(tabs.TabGroup):
    slug = "containers_and_docker_hosts"
    tabs = (ContainerTab, HostTab)
    sticky = True
