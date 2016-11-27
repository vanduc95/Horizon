from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.service_management.container_service. \
    service.docker_api import docker_api
from openstack_dashboard.dashboards.service_management.container_service. \
    database import services as database_service
from horizon import forms
from horizon import messages
import time
from openstack_dashboard.dashboards.service_management.container_service.database import services as db_service
from django.utils.safestring import mark_safe
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

    def clean(self):
        cleaned_data = super(CreateServiceForm, self).clean()
        services_name = []
        for service in db_service.db_session.query(db_service.Service).all():
            services_name.append(service.service_name)
        # list_service = ['1', '2', '3', '4', '5']

        # Validate name service
        if self.data['service_name'] and (self.data['service_name'] in services_name):
            msg = _("Name service exists!")
            self._errors['service_name'] = self.error_class([msg])
            self.data['container_number'] = 'Select container number'
            return cleaned_data

        # Validate info about containers
        if self.data['container_number']:
            msg = ''
            containers_name_input = []

            for i in range(int(self.data['container_number'])):
                error = False
                mes = ''
                # if self.data['container_IP' + str(i)]:
                # if

                if self.data['container_Internal_External_Port' + str(i)]:
                    int_ext_port = self.data['container_Internal_External_Port' + str(i)]
                    for obj in int_ext_port.split(';'):
                        if len(obj.split(':')) != 2:
                            mes += 'container_Internal_External_Port wrong format' + '<br/>'
                            error = True
                            break

                if self.data['container_environment' + str(i)]:
                    env = self.data['container_environment' + str(i)]
                    for obj in env.split(';'):
                        if len(obj.split(':')) != 2:
                            mes += 'container environment wrong format' + '<br/>'
                            error = True
                            break

                if error:
                    mes = '<b>Container' + str(i) + '</b><br/>' + mes
                    msg += mes

            # Validate duplicate container name
            for i in range(int(self.data['container_number'])):
                containers_name_input.append(self.data['container_name' + str(i)])
            if len(containers_name_input) != len(set(containers_name_input)):
                msg += '<br>Error duplicate name containers'
            else:
                cli = docker_api.connect_docker()
                for ct in cli.containers(all=True):
                    name = ct['Names'][0][1:]
                    if name in containers_name_input:
                        msg += '<br>Name container exits!'

            # If have error
            if msg != '':
                self.data['container_number'] = 'Select container number'
                raise forms.ValidationError(mark_safe(msg))
                return cleaned_data

        return cleaned_data

    def handle(self, request, data):
        # first_service = db_service.db_session.\
        # query(ctn_service.Service).first()
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

            container['ip'] = request.POST['container_IP' + suffix]
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
            for container in containers:
                network_config = cli.create_networking_config({
                    network_name: cli.create_endpoint_config(ipv4_address=container['ip'])
                })
                ports = []
                port_bindings = {}
                for port in container['port']:
                    arr = port.split(':')
                    ports.append(arr[0])
                    if arr[1] == 'None':
                        port_bindings[arr[0]] = None
                    else:
                        port_bindings[arr[0]] = arr[1]

                host_config = cli.create_host_config(port_bindings=port_bindings)
                if network_name == 'bridge':
                    container = cli.create_container(
                        name=container['name'],
                        command=container['command'],
                        host_config=host_config,
                        environment=container['environment'],
                        ports=ports,
                        image=container['image'])
                    cli.start(container)
                    container_run_success.append(container['Id'])
                else:
                    container = cli.create_container(
                        name=container['name'],
                        command=container['command'],
                        networking_config=network_config,
                        host_config=host_config,
                        environment=container['environment'],
                        ports=ports,
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
            msg = None
            if network_name == 'bridge':
                msg = 'Create service successful. With bridge network, ip container not support defined by user'
            else:
                msg = 'Create service successful'
            messages.success(request, msg)
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
