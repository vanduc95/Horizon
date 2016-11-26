from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.service_management.container_service.\
    service.docker_api import docker_api
from openstack_dashboard.dashboards.service_management.container_service.\
    database import services as database_service
from horizon import forms
from horizon import messages
import time
from django.core.urlresolvers import reverse
from horizon import exceptions


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
    network = forms.ChoiceField(
        label=_("Network for Containers"), required=True)
    container_number = forms.ChoiceField(label=_("Container Number"),
                                         required=True,
                                         choices=NUM_CHOICE, )

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceForm, self).__init__(self, *args, **kwargs)
        cli = docker_api.connect_docker()
        list_network = [('', _("Select network"))]
        for network in cli.networks():
            net = []
            net.append(network['Id'])
            net.append(network['Name'])
            list_network.append(net)
        self.fields['network'].choices = list_network

        request.session['test'] = 'vanduc'
        request.session.set_expiry(3600 * 24)

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
        container_run_success = []
        try:
            cli = docker_api.connect_docker()
            networks = cli.networks(ids=[service_config['networkID'], ])
            network = networks[0]
            network_name = network['Name']
            network_config = cli.create_networking_config({
                network_name: cli.create_endpoint_config()
            })
            for container in containers:
                container = cli.create_container(
                    name=container['name'],
                    command=container['command'],
                    networking_config=network_config,
                    environment=container['environment'],
                    ports=container['port'],
                    image=container['image'])
                cli.start(container)
                container_run_success.append(container['Id'])
            time.sleep(10)

            db_service = database_service.DatabaseService()
            service = database_service.Service(service_name=service_name)

            for container in container_run_success:
                container_db = database_service.Container(
                    container_id=container)
                service.container.append(container_db)

            db_service.add_service(service)
            db_service.close()
            messages.success(request, 'Create service successful')
            return True
        except Exception as e:
            cli = docker_api.connect_docker()
            for container_id in container_run_success:
                cli.stop(container_id)
                time.sleep(3)
                cli.remove_container(container_id)
            redirect = reverse(
                "horizon:service_management:container_service:index")

            exceptions.handle(request,
                              _(e.explanation),
                              redirect=redirect)
            return False
