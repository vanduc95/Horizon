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
from docker import Client
from horizon import views
import django.views
import json
from django.http import HttpResponse  # noqa
import datetime
import time

from openstack_dashboard.dashboards.docker_swarm.chart.cadvisor_api import docker_api
import time


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'docker_swarm/chart/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        containers_info = docker_api.get_all_container_data(host_ip='127.0.0.1')
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
        container_list = []
        cli = Client(base_url='tcp://127.0.0.1:2376')
        for container in cli.containers():
            container_list.append({'id': container['Id']})
        return HttpResponse(json.dumps(container_list), content_type='application/json')


def get_interval(current, previous):
    cur = datetime.datetime.strptime(current[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    prev = datetime.datetime.strptime(previous[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    return (cur - prev).total_seconds() * 1000000000
