# Copyright 2012 NEC Corporation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import docker
import logging
import netaddr
from docker import Client
from horizon import exceptions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import workflows
from horizon import forms
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database

LOG = logging.getLogger(__name__)


class CreateNetworkInfoAction(workflows.Action):
    host_id = forms.ChoiceField(label=_("Host"), required=True)
    network_name = forms.CharField(max_length=100, label=_("Network Name"),
                                   required=True)
    is_internal = forms.BooleanField(label="Enable Internal", initial=False, required=False)
    set_subnet = forms.BooleanField(label=_("Set Network Information"),
                                    widget=forms.CheckboxInput(attrs={
                                        'class': 'switchable',
                                        'data-slug': 'with_subnet',
                                        'data-hide-tab': 'create_network__'
                                                         'createsubnetinfo'
                                                         'action',
                                        'data-hide-on-checked': 'false'
                                    }),
                                    initial=True,
                                    required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(CreateNetworkInfoAction, self).__init__(request, context, *args,
                                                      **kwargs)
        db_service = docker_host_database.DataService()

        host_choice = [('', _("Select Host which places network"))]
        for host in db_service.session.query(docker_host_database.DockerHost).order_by(
                docker_host_database.DockerHost.id):
            host_choice.append((host.id, host.host_name))
        self.fields['host_id'].choices = host_choice

    class Meta(object):
        name = _("Network")
        help_text = _('Create a new network. '
                      'In addition, a subnet associated with the network '
                      'can be created in the following steps of this wizard.')


class CreateNetworkInfo(workflows.Step):
    action_class = CreateNetworkInfoAction
    contributes = ("network_name", 'is_internal', "set_subnet", 'host_id')


class CreateSubnetInfoAction(workflows.Action):
    network_address = forms.IPField(label=_("Network Address"),
                                    required=False,
                                    initial="",
                                    widget=forms.TextInput(attrs={
                                        'class': 'switched',
                                        'data-switch-on': 'source',
                                        'data-source-manual': _("Network Address"),
                                    }),
                                    help_text=_("Network address in CIDR format V4"
                                                "(e.g. 192.168.0.0/24)"),
                                    version=forms.IPv4,
                                    mask=True)
    ip_range = forms.IPField(label=_("IP range"),
                             required=False,
                             initial="",
                             widget=forms.TextInput(attrs={
                                 'class': 'switched',
                                 'data-switch-on': 'ip_range',
                                 'data-source-manual': _("IP range"),
                             }),
                             help_text=_("IP range in CIDR format V4"
                                         "(e.g. 192.168.0.0/24)"),
                             version=forms.IPv4,
                             mask=True)
    default_ip_range = forms.BooleanField(label=_("Use Default IP range"),
                                          widget=forms.CheckboxInput(attrs={
                                              'class': 'switchable',
                                              'data-slug': 'ip_range',
                                              'data-hide-on-checked': 'true'
                                          }),
                                          initial=False,
                                          required=False)
    gateway_ip = forms.IPField(
        label=_("Gateway IP"),
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'gateway_ip',
            'data-source-manual': _("Gateway IP")
        }),
        required=False,
        initial="",
        help_text=_("IP address of Gateway (e.g. 192.168.0.254) "
                    "The default value is the first IP of the "
                    "network address "
                    "(e.g. 192.168.0.1 for 192.168.0.0/24, "
                    "2001:DB8::1 for 2001:DB8::/48). "
                    "If you use the default, leave blank. "
                    "If you do not want to use a gateway, "
                    "check 'Disable Gateway' below."),
        version=forms.IPv4,
        mask=False)

    default_gate_way = forms.BooleanField(label=_("Use Default Gateway"),
                                          widget=forms.CheckboxInput(attrs={
                                              'class': 'switchable',
                                              'data-slug': 'gateway_ip',
                                              'data-hide-on-checked': 'true'
                                          }),
                                          initial=False,
                                          required=False)

    class Meta(object):
        name = _("Subnet")
        help_text = _('Set Subnet for network.')

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetInfoAction, self).__init__(request, context, *args,
                                                     **kwargs)
        if 'set_subnet' in context:
            self.fields['set_subnet'] = forms.BooleanField(
                initial=context['set_subnet'],
                required=False,
                widget=forms.HiddenInput()
            )

    def _check_subnet_data(self, cleaned_data, is_create=True):
        network_address = cleaned_data.get('network_address')
        ip_range = cleaned_data.get('ip_range')
        gateway_ip = cleaned_data.get('gateway_ip')
        default_ip_range = cleaned_data.get('default_ip_range')
        default_gateway = cleaned_data.get('default_gate_way')

        # When creating network from a pool it is allowed to supply empty
        # subnetpool_id signaling that Neutron should choose the default
        # pool configured by the operator. This is also part of the IPv6
        # Prefix Delegation Workflow.
        if not network_address:
            msg = _('Specify "Network Address" or'
                    'clear "Set Network Information" checkbox in previous step.')
            raise forms.ValidationError(msg)
        if network_address:
            subnet = netaddr.IPNetwork(network_address)
            if subnet.version == 4 and subnet.prefixlen == 32:
                msg = _("The subnet in the Network Address is "
                        "too small (/%s).") % subnet.prefixlen
                self._errors['network_address'] = self.error_class([msg])
                raise forms.ValidationError(msg)
        if not default_ip_range and not ip_range:
            msg = _('Specify IP Network Range or '
                    'check "Use Default IP range" checkbox.')
            raise forms.ValidationError(msg)
        if not default_ip_range and ip_range and netaddr.IPNetwork(ip_range) not in netaddr.IPNetwork(network_address):
            msg = _('IP Range must be subset of Network Address')
            raise forms.ValidationError(msg)

        if not default_gateway and not gateway_ip:
            msg = _('Specify Gateway IP or '
                    'check "Use Default Gateway" checkbox.')
            raise forms.ValidationError(msg)
        if not default_gateway and gateway_ip and netaddr.IPNetwork(gateway_ip) not in netaddr.IPNetwork(
                network_address):
            msg = _('Gateway IP must be in Network Address')
            raise forms.ValidationError(msg)

    def clean(self):
        cleaned_data = super(CreateSubnetInfoAction, self).clean()
        set_subnet = cleaned_data.get('set_subnet')
        if not set_subnet:
            return cleaned_data
        self._check_subnet_data(cleaned_data)
        return cleaned_data


class CreateSubnetInfo(workflows.Step):
    action_class = CreateSubnetInfoAction
    contributes = ("network_address", "ip_range",
                   "gateway_ip", "default_ip_range",
                   "default_gate_way")


class CreateNetwork(workflows.Workflow):
    slug = "create_network"
    name = _("Create Network")
    finalize_button_name = _("Create")
    success_message = _('Created network "%s".')
    failure_message = _('Unable to create network "%s".')
    default_steps = (CreateNetworkInfo,
                     CreateSubnetInfo)
    wizard = True

    def get_success_url(self):
        return reverse("horizon:docker_management:networks:index")

    def get_failure_url(self):
        return reverse("horizon:docker_management:networks:index")

    def format_status_message(self, message):
        name = self.context.get('network_name')
        return message % name

    def handle(self, request, data):
        try:
            db_service = docker_host_database.DataService()
            docker_host = db_service.session.query(docker_host_database.DockerHost). \
                filter_by(id=data["host_id"]).first()
            docker_cli = Client(base_url='tcp://' + docker_host.host_url + ':2376')
            if data['set_subnet']:
                gateway = None
                iprange = None
                subnet = data['network_address']
                if not data['default_gate_way']:
                    gateway = data['gateway_ip']
                else:
                    gateway = str(netaddr.IPNetwork(data['network_address'])[1])
                if not data['default_ip_range']:
                    iprange = data['ip_range']
                ipam_pool = docker.utils.create_ipam_pool(
                    subnet=subnet,
                    gateway=gateway,
                    iprange=iprange
                )
                ipam_config = docker.utils.create_ipam_config(
                    pool_configs=[ipam_pool]
                )
                docker_cli.create_network(data['network_name'], driver="bridge", ipam=ipam_config)
            else:
                docker_cli.create_network(data['network_name'], driver="bridge")
            return True

        except Exception as e:
            msg = _('Failed to create network "%(net)s": '
                    ' %(reason)s')
            redirect = self.get_failure_url()
            exceptions.handle(request,
                              msg % {"net": data['network_name'],
                                     "reason": e},
                              redirect=redirect)
            return False
