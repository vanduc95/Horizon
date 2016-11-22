from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.service_management.container_service.service.docker_api import docker_api
from horizon import forms


class CreateServiceForm(forms.SelfHandlingForm):
    NUM_CHOICE = [('2',_('2')),
                  ('3',_('3')),
                  ('4',_('4')),
                  ('5',_('5')),
                  ('6',_('6')),]
    service_name = forms.CharField(max_length=255,
                                   label=_("Name Service"),
                                   required=True)
    network = forms.ChoiceField(label=_("Choose network"),
                                required=False)
    container_number = forms.ChoiceField(label=_("Number Container"),
                                         required=False,
                                         choices=NUM_CHOICE,)

    def __init__(self,request,*args,**kwargs):
        super(CreateServiceForm, self).__init__(self, *args, **kwargs)
        cli = docker_api.connect_docker()
        list_network = []
        for network in cli.networks():
            net = []
            net.append(network['Id'])
            net.append(network['Name'])
            list_network.append(net)
        self.fields['network'].choices = list_network

    def handle(self, request, data):
        return True
