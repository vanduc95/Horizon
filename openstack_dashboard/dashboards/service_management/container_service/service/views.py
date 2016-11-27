from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.service_management.container_service.service import forms as create_forms
from django.core.urlresolvers import reverse
from horizon import exceptions
from horizon import views
from docker import Client
import django.views
from django.http import HttpResponse
import json


class CreateService(forms.ModalFormView):
    form_class = create_forms.CreateServiceForm
    form_id = "create_service_form"
    modal_header = _("Create An Service")
    submit_url = reverse_lazy('horizon:service_management:container_service:service:create')
    template_name = 'service_management/container_service/service/create.html'
    success_url = reverse_lazy("horizon:service_management:container_service:index")
    page_title = _("Create An Service")


class ImageDockerRequest(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        cli = Client(base_url='unix://var/run/docker.sock')
        image_docker = []
        for image in cli.images():
            if image['RepoTags'] != None:
                repo = image['RepoTags']
                repoTags = repo[0]
                image_docker.append({'name_image': repoTags})

        return HttpResponse(json.dumps(image_docker), content_type='application/json')


class NetworkDetailRequest(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        network_id = request.GET.get('id', None)
        cli = Client(base_url='unix://var/run/docker.sock')
        network_info = cli.networks(ids=[network_id, ])[0]
        name = network_info['Name']
        try:
            subnet = network_info['IPAM']['Config'][0]['Subnet']
        except:
            subnet = 'None'
        try:
            gateway = network_info['IPAM']['Config'][0]['Gateway']
        except:
            gateway = 'None'

        network_detail = {'name': name, 'subnet': subnet, 'gateway': gateway}


        return HttpResponse(json.dumps(network_detail), content_type='application/json')
