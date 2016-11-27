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
import json
from django.http import HttpResponse
# from django.http import Http404
import datetime
# import time
from openstack_dashboard.dashboards.service_management.container_service\
    .chart import cadvisor_api

HOST_IP = '127.0.0.1'


class ContainerCPUDetailView(django.views.generic.TemplateView):

    def get(self, request, *args, **kwargs):
        container_id = request.GET.get('id', None)
        container_data = cadvisor_api.get_container_detail(
            host_ip=HOST_IP, container_id=container_id)
        if container_data != 'Error':
            container_name = container_data['name']
            containers_info = container_data['realtime_data']
            data_timestamp_list = []
            data = {}
            data['name'] = container_name
            data['unit'] = 'Cores'
            index = 1
            data_list = containers_info['/docker/' + container_id]
            while index < len(data_list):
                cur = data_list[index]
                prev = data_list[index - 1]
                interval_nano = get_interval(
                    cur['timestamp'], prev['timestamp'])
                cpu_usage = (cur['cpu']['usage']['total'] -
                             prev['cpu']['usage']['total']) / interval_nano
                data_timestamp_list.append(
                    {'y': cpu_usage, 'x': cur['timestamp']})
                index += 1
            data['value'] = data_timestamp_list
            data['id'] = container_id
            return HttpResponse(json.dumps(data),
                                content_type='application/json')

        else:
            context = {
                'status': '400',
                'reason': 'Cannot retreive container data from cadvisor_api'
            }
            response = HttpResponse(json.dumps(context),
                                    content_type='application/json')
            response.status_code = 400
            return response


class ContainerRAMDetailView(django.views.generic.TemplateView):

    def get(self, request, *args, **kwargs):
        container_id = request.GET.get('id', None)
        container_data = cadvisor_api.get_container_detail(
            host_ip=HOST_IP, container_id=container_id)
        if container_data != 'Error':
            container_name = container_data['name']
            container_ram_data = container_data['realtime_data']
            data_timestamp_list = []
            data = {}
            data['name'] = container_name
            data['unit'] = 'MB'
            for value_unit in container_ram_data['/docker/' + container_id]:
                data_timestamp_list.append(
                    {'y': float(value_unit['memory']['usage']) / (1024 * 1024),
                     'x': value_unit['timestamp']})
            data['value'] = data_timestamp_list
            data['id'] = container_id
            return HttpResponse(json.dumps(data),
                                content_type='application/json')
        else:
            context = {
                'status': '400',
                'reason': 'Cannot retreive container data from cadvisor_api'
            }
            response = HttpResponse(json.dumps(context),
                                    content_type='application/json')
            response.status_code = 400
            return response


class ContainerListView(django.views.generic.TemplateView):

    def get(self, request, *args, **kwargs):
        container_list = []
        container_list_data = cadvisor_api.get_container_list(HOST_IP)
        if container_list_data != "Error":
            for container in container_list_data:
                container_list.append({'id': container['Id']})
            return HttpResponse(json.dumps(container_list),
                                content_type='application/json')
        else:
            context = {
                'status': '400',
                'reason': 'cannot get container list from Docker Client'
            }
            response = HttpResponse(json.dumps(context),
                                    content_type='application/json')
            response.status_code = 400
            return response


def get_interval(current, previous):
    cur = datetime.datetime.strptime(current[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    prev = datetime.datetime.strptime(previous[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    return (cur - prev).total_seconds() * 1000000000
