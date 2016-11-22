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

INFO_DETAIL_TEMPLATE_NAME = 'horizon/common/_detail_table.html'


class ContainerTab(tabs.TableTab):
    table_classes = (container_tables.ContainerTable,)
    name = container_tables.ContainerTable.Meta.verbose_name
    slug = container_tables.ContainerTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    def get_containers_data(self):
        return []


class ServiceTab(tabs.TableTab):
    table_classes = (service_tables.ServiceTable,)
    name = service_tables.ServiceTable.Meta.verbose_name
    slug = service_tables.ServiceTable.Meta.name
    template_name = INFO_DETAIL_TEMPLATE_NAME

    class DockerHostData:
        def __init__(self, id, name, host_ip):
            self.id = id
            self.name = name
            self.host_ip = host_ip

    def get_services_data(self):
        return []


class ContainerAndServiceTabs(tabs.TabGroup):
    slug = "container_and_service"
    tabs = (ContainerTab, ServiceTab)
    sticky = True
