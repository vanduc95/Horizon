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

import django.views
from docker import Client
from openstack_dashboard.dashboards.docker_swarm.service_monitor import tables as tbl_service_monitor
from django.utils.translation import ugettext_lazy as _
from horizon import tables
from openstack_dashboard.dashboards.docker_swarm.service_monitor.cadvisor_api import docker_api
import time
import json
from django.http import HttpResponse
import datetime


class Container:
    def __init__(self, containerId, image, command, created, state, name, host_ip):
        self.id = containerId
        self.image = image
        self.command = command
        self.created = created
        self.state = state
        self.name = name
        self.host_ip = host_ip


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'docker_swarm/service_monitor/index.html'
    table_class = tbl_service_monitor.ContainerInServiceTable
    page_title = _("Service Monitor")

    def get_data(self):
        host_ip = ['0.0.0.0', '192.168.2.128']

        cli = Client(base_url='unix://var/run/docker.sock')
        services = []
        for service in cli.services():
            name = service['Spec']['Name']
            services.append(name)
        containers = []
        if self.request.method == 'GET' and 'service' in self.request.GET \
                and self.request.GET['service'] in services:
            serviceName = self.request.GET['service']
            for ip in host_ip:
                try:
                    cli = Client(base_url='tcp://' + ip + ':2376')
                    dict_container = cli.containers(all=True)
                    for ct in dict_container:
                        if len(ct['Labels'].keys()) != 0 \
                                and ct['Labels']['com.docker.swarm.service.name'] == serviceName:
                            # convert data
                            created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
                            name = ct['Names'][0][1:]
                            containers.append(
                                Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name, ip))
                except:
                    print 'Cant connect', ip
            return containers
        else:
            return containers

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        cli = Client(base_url='unix://var/run/docker.sock')
        services = []
        for service in cli.services():
            name = service['Spec']['Name']
            services.append(name)

        context['services'] = services

        if self.request.method == 'GET' and 'service' in self.request.GET:
            # and self.request.GET['service'] in context['services']
            context['selected'] = self.request.GET['service']
        else:
            context['selected'] = '-1'
        return context


class ContainerCPUDetailView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        container_list = []
        cli = Client(base_url='tcp://127.0.0.1:2376')
        container_id = request.GET.get('id', None)
        container_name = cli.containers(filters={"id": container_id})[0]['Names'][0]
        containers_info = docker_api.get_container_detail(host_ip='127.0.0.1', container_id=container_id)
        data_timestamp_list = []
        data = {}
        data['name'] = container_name
        data['unit'] = 'Cores'
        index = 1
        data_list = containers_info['/docker/' + container_id]
        while index < len(data_list):
            cur = data_list[index]
            prev = data_list[index - 1]
            interval_nano = get_interval(cur['timestamp'], prev['timestamp'])
            cpu_usage = (cur['cpu']['usage']['total'] - prev['cpu']['usage']['total']) / interval_nano
            data_timestamp_list.append(
                {'y': cpu_usage, 'x': cur['timestamp']})
            index += 1
        data['value'] = data_timestamp_list
        data['id'] = container_id
        return HttpResponse(json.dumps(data), content_type='application/json')


class ContainerRAMDetailView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        container_list = []
        cli = Client(base_url='tcp://127.0.0.1:2376')
        container_id = request.GET.get('id', None)
        container_name = cli.containers(filters={"id": container_id})[0]['Names'][0]
        containers_info = docker_api.get_container_detail(host_ip='127.0.0.1', container_id=container_id)
        data_timestamp_list = []
        data = {}
        data['name'] = container_name
        data['unit'] = 'MB'
        for value_unit in containers_info['/docker/' + container_id]:
            data_timestamp_list.append(
                {'y': float(value_unit['memory']['usage']) / (1024 * 1024), 'x': value_unit['timestamp']})
        data['value'] = data_timestamp_list
        data['id'] = container_id
        return HttpResponse(json.dumps(data), content_type='application/json')


class ContainerListView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.method == 'GET' and 'service' in self.request.GET:
            print self.request.GET['service']
        container_list = []
        cli = Client(base_url='tcp://127.0.0.1:2376')
        for container in cli.containers():
            container_list.append({'id': container['Id']})
        return HttpResponse(json.dumps(container_list), content_type='application/json')


def get_interval(current, previous):
    cur = datetime.datetime.strptime(current[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    prev = datetime.datetime.strptime(previous[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    return (cur - prev).total_seconds() * 1000000000