from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.service_management.container_service.service.docker_api import docker_api
from openstack_dashboard.dashboards.service_management.container_service.database import services as database_service
from horizon import forms
from horizon import messages
import time

class CreateServiceForm(forms.SelfHandlingForm):
    NUM_CHOICE = [
        ('', _("Select container numbers")),
        ('1', _('1')),
        ('2', _('2')),
        ('3', _('3')),
        ('4', _('4')),
        ('5', _('5')),
        ('6', _('6')), ]
    service_name = forms.CharField(max_length=255,
                                   label=_("Service Name"),
                                   required=True)
    network = forms.ChoiceField(label=_("Network for Containers"))
    container_number = forms.ChoiceField(label=_("Container Number"),
                                         required=True,
                                         choices=NUM_CHOICE, )

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceForm, self).__init__(self, *args, **kwargs)
        cli = docker_api.connect_docker()
        list_network = [('', _("Select image which will be used for create new container"))]
        for network in cli.networks():
            net = []
            net.append(network['Id'])
            net.append(network['Name'])
            list_network.append(net)
        self.fields['network'].choices = list_network

    def handle(self, request, data):
        containers = []
        networkID = request.POST["network"]
        service_name = request.POST["service_name"]
        num_of_container = int(request.POST['container_number'])
        for i in range(0, num_of_container):
            suffix = str(i)
            container = {}
            container['name'] = request.POST['container_name' + suffix]
            container['image'] = request.POST['container_image' + suffix]
            env = request.POST['container_environment' + suffix]
            arr_env = env.split(';')
            container['environment'] = arr_env

            container['command'] = request.POST['container_command' + suffix]
            ports = request.POST['container_Internal_External_Port' + suffix]
            container['port'] = ports.split(';')

            container['id'] = request.POST['container_IP' + suffix]
            containers.append(container)
        service_config = {
            'service_name': service_name,
            'networkID': networkID,
            'containers': containers,
        }
        create_action = docker_api.create_service(service_config)
        time.sleep(10)
        if create_action:
            db_service = database_service.Database_service()
            service_id = db_service.get_service_id()
            for container in containers:
                service =database_service.Service(name_service=service_name, container_id=container['id'], service_id=service_id)
                db_service.add_service(service)
            db_service.close()
            messages.success(request,'create service successful')
            return True
        else:
            return False
