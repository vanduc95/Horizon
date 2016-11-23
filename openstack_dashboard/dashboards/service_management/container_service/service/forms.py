from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.service_management.container_service.service.docker_api import docker_api
from horizon import forms


class CreateServiceForm(forms.SelfHandlingForm):
    NUM_CHOICE = [        
                  ('', _("Select container numbers")),
                  ('2',_('2')),
                  ('3',_('3')),
                  ('4',_('4')),
                  ('5',_('5')),
                  ('6',_('6')),]
    service_name = forms.CharField(max_length=255,
                                   label=_("Service Name"),
                                   required=True)
    network = forms.ChoiceField(label=_("Network for Containers"))
    container_number = forms.ChoiceField(label=_("Container Number"),
                                         required=True,
                                         choices=NUM_CHOICE,)

    def __init__(self,request,*args,**kwargs):
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
        request.session.set_expiry(3600*24)

    def handle(self, request, data):
        # print request.
        return True
