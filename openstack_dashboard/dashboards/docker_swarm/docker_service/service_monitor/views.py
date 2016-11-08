from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.docker_swarm.docker_service.service_monitor import forms as create_forms

import django.views
from docker import Client
from openstack_dashboard.dashboards.docker_swarm.docker_service.service_monitor.cadvisor_api import docker_api
import json
from django.http import HttpResponse
import datetime


class ConfigScaleForm(forms.ModalFormView):
    form_class = create_forms.ConfigScale
    form_id = "config_scale_form"
    modal_header = _("Config Auto Scale")
    submit_url = reverse_lazy('horizon:docker_swarm:docker_service:service_monitor:config')
    template_name = 'docker_swarm/docker_service/service_monitor/create.html'
    success_url = reverse_lazy("horizon:docker_swarm:docker_service:index")
    page_title = _("Config Scale")


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