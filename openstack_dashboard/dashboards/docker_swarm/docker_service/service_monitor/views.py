from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.docker_swarm.docker_service.service_monitor import forms as create_forms

import django.views
from docker import Client
from openstack_dashboard.dashboards.docker_swarm.docker_service.service_monitor.cadvisor_api import docker_api
import json
import requests
from django.http import HttpResponse
import datetime
from openstack_dashboard.dashboards.docker_swarm.docker_service.scale_services import service as service_scale

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


class ScaleActionRequest(django.views.generic.TemplateView):
    def get(self,request,*args,**kwargs):
        cli = Client(base_url='tcp://127.0.0.1:2376')
        option = request.GET.get('option',None)
        service_name = request.GET.get('service_id', None)

        for service in cli.services():
            if service['Spec']['Name'] == service_name:
                service_id = service['ID']
                break
        scale = service_scale.scale(service_id,None,option=option)
        if scale:
            result = {'result':True}
        else:
            result = {'result':False}
        return HttpResponse(json.dumps(result),content_type='application/json')

class ServiceResourceDetail(django.views.generic.TemplateView):
    def get(self,request,*args,**kwargs):
        service_name = request.GET.get('service_id',None)
        cli = Client(base_url='tcp://127.0.0.1:2376')
        list_container = cli.containers()
        list_container_of_service = []
        for container in list_container:
            if container['Labels'] and container['Labels']['com.docker.swarm.service.name'] == service_name:
                list_container_of_service.append(container['Id'])

        response = requests.get('http://127.0.0.1:8080/api/v1.2/docker/')
        # containers = docker_api.get_all_container_data('127.0.0.1')
        containers = response.json()
        result = {}
        for container in containers:
            if containers[container]['id'] in list_container_of_service:
                stats = []
                for status in containers[container]['stats']:
                    element_stats = {}
                    element_stats['timestamp'] = status['timestamp'][:19]
                    element_stats['cpu'] = status['cpu']['usage']['total']
                    element_stats['ram'] = status['memory']['usage']
                    stats.append(element_stats)
                result[containers[container]['id']] = stats
        return HttpResponse(json.dumps(result),content_type='application/json')

class ModeScaleContainer(django.views.generic.TemplateView):
    def get(self,request,*args,**kwargs):
        cli = Client(base_url='tcp://127.0.0.1:2376')
        services = cli.services()
        result = ''
        service_id= ''
        service_name = request.GET.get('service_id',None)

        for service in services:
            if service['Spec']['Name']==service_name:
                service_id = service['ID']
                break

        if request.session.has_key('config'):
            config = request.session['config']
            check_service = False
            for key in config:
                if key == service_id:
                    result = config[key]
                    check_service = True
                    break
            if not check_service:
                result ={'result':False}
        else:
            result = {'result':False}

        print result
        return HttpResponse(json.dumps(result), content_type='application/json')

# class UsageContainer(django.views.generic.TemplateView):
#     def get(self,request,*args,):

def get_interval(current, previous):
    cur = datetime.datetime.strptime(current[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    prev = datetime.datetime.strptime(previous[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    return (cur - prev).total_seconds() * 1000000000