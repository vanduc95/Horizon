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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from docker import Client

from horizon import forms
from horizon import workflows
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database

LOG = logging.getLogger(__name__)


class CreateContainerInfoAction(workflows.Action):
    host_id = forms.ChoiceField(label=_("Host"), required=True)
    container_name = forms.CharField(max_length=255,
                                     label=_("Container Name"),
                                     required=False)
    image_source = forms.ChoiceField(
        label=_("Image Source"),
        help_text=_("Choose Image which is base of new container"),
        choices=[('local', _('From Local')),
                 ('repository', _('From Repository'))],
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'image_source'
        }))

    image_local = forms.ChoiceField(
        label=_("Host"),
        required=False,
        help_text=_("Local image"),
        widget=forms.Select(attrs={
            'class': 'switched',
            'data-switch-on': 'image_source',
            'data-image_source-local': _('Image Local')
        })
    )

    image_repository = forms.CharField(
        max_length=255,
        required=False,
        label=_("Repository Image"),
        help_text=_("Repository image"),
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'image_source',
            'data-image_source-repository': _('Image Repo'),
            'placeholder': 'Type image name in repository'
        }))
    command = forms.CharField(
        max_length=255,
        required=False,
        label=_("Command string"),
        help_text=_("Command string for new container"))
    set_network = forms.BooleanField(label=_("Set Network Information"),
                                     widget=forms.CheckboxInput(attrs={
                                         'class': 'switchable',
                                         'data-slug': 'with_subnet',
                                         'data-hide-tab': 'create_container__'
                                                          'setcontainernetworkinfoaction',
                                         'data-hide-on-checked': 'false'
                                     }),
                                     initial=True,
                                     required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(CreateContainerInfoAction, self).__init__(request, context, *args,
                                                        **kwargs)
        db_service = docker_host_database.DataService()

        host_choice = [('', _("Select Host which places new Container"))]
        for host in db_service.session.query(docker_host_database.DockerHost).order_by(
                docker_host_database.DockerHost.id):
            host_choice.append((host.id, host.host_name))
        self.fields['host_id'].choices = host_choice

        images_choice = [('', _("Select image which will be used for create new container"))]
        for host in db_service.session.query(docker_host_database.DockerHost).order_by(
                docker_host_database.DockerHost.id):
            docker_cli = Client(base_url='tcp://' + host.host_url + ':2376')
            for image in docker_cli.images():
                images_choice.append(
                    (image['Id'] + ":" + str(host.id),
                     CreateContainerInfoAction.get_images_name(image['RepoTags'], image['Id'])))
        self.fields['image_local'].choices = images_choice

    def clean(self):
        cleaned_data = super(CreateContainerInfoAction, self).clean()
        image_source = cleaned_data.get('image_source')
        if image_source == 'local':
            image_local = cleaned_data.get('image_local')
            if not image_local:
                msg = _('Specify Image which will be used')
                self._errors['image_local'] = self.error_class([msg])
                raise forms.ValidationError(msg)
        elif image_source == 'repository':
            image_repository = cleaned_data.get('image_repository')
            if not image_repository:
                msg = _('Specify Image which will be used')
                self._errors['image_repository'] = self.error_class([msg])
                raise forms.ValidationError(msg)
        return cleaned_data

    @staticmethod
    def get_images_name(image_names,id):
        image_join_names = ''
        if isinstance(image_names, list):
            for name in image_names:
                image_join_names += name
        else:
            image_join_names+=id
        return image_join_names

    class Meta(object):
        name = _("Container Information")
        help_text = _('Create a new container')


class CreateContainerInfo(workflows.Step):
    action_class = CreateContainerInfoAction
    contributes = ("container_name", 'host_id', 'image_source', 'image_local', 'image_repository', 'set_network')


class SetContainerNetworkInfoAction(workflows.Action):
    network_id = forms.ChoiceField(
        label=_("Network"),
        help_text=_("Select network which container will be connected to"),
        required=False
    )
    expose_ports = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("Exposed Ports And Ports Binding"),
        help_text=_("Each port in one line,"
                    "ExposedPort and port Bindings seperate by comma, example 8080:80,90,5000"),
        required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(SetContainerNetworkInfoAction, self).__init__(request, context, *args,
                                                            **kwargs)
        if 'set_network' in context:
            self.fields['set_network'] = forms.BooleanField(
                initial=context['set_network'],
                required=False,
                widget=forms.HiddenInput()
            )
        db_service = docker_host_database.DataService()
        network_choice = [('', _("Select network which container will be connected to"))]
        for host in db_service.session.query(docker_host_database.DockerHost).order_by(
                docker_host_database.DockerHost.id):
            docker_cli = Client(base_url='tcp://' + host.host_url + ':2376')
            for network in docker_cli.networks():
                network_choice.append(
                    (network['Id'] + ":" + str(host.id), SetContainerNetworkInfoAction.get_network_name(network)))
        self.fields['network_id'].choices = network_choice

    def clean(self):
        cleaned_data = super(SetContainerNetworkInfoAction, self).clean()
        set_network = cleaned_data.get('set_network')
        if set_network:
            net_id = cleaned_data.get('network_id')
            if not net_id:
                msg = _('Specify Network which will be used')
                self._errors['network_id'] = self.error_class([msg])
                raise forms.ValidationError(msg)
        return cleaned_data

    @staticmethod
    def get_network_name(network):
        network_name = network['Name'] + " : "
        for subnet in network['IPAM']['Config']:
            network_name += subnet['Subnet']
        return network_name

    class Meta(object):
        name = _("Network Setting")
        help_text = _('Setting network for new container')


class SetNetworkInfo(workflows.Step):
    action_class = SetContainerNetworkInfoAction
    contributes = ("network_id", 'expose_ports')


class SetContainerOptionAction(workflows.Action):
    is_enable_stdin = forms.BooleanField(label=_("Keep STDIN open"), initial=False,
                                         required=False)
    is_enable_pseudo_TTY = forms.BooleanField(label=_("Allocate a pseudo-TTY"), initial=False,
                                              required=False)
    is_detach = forms.BooleanField(label=_("Enable Detach"), initial=False,
                                   required=False)
    working_dir = forms.CharField(max_length=255,
                                  label=_("Working directory"),
                                  required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(SetContainerOptionAction, self).__init__(request, context, *args,
                                                       **kwargs)

    class Meta(object):
        name = _("Container Option")
        help_text = _('Set Option for this container')


class SetContainerOption(workflows.Step):
    action_class = SetContainerOptionAction
    contributes = ("is_enable_stdin", "is_enable_pseudo_TTY", "is_detach", "working_dir")


class CreateRunningContainer(workflows.Workflow):
    slug = "create_container"
    name = _("Create Container")
    finalize_button_name = _("Create And Run")
    success_message = _('Created Running Container "%s".')
    failure_message = _('Unable to create and run Container "%s".')
    default_steps = (CreateContainerInfo,
                     SetNetworkInfo, SetContainerOption)
    wizard = True

    def get_success_url(self):
        return reverse("horizon:docker_management:containers:index")

    def get_failure_url(self):
        return reverse("horizon:docker_management:containers:index")

    def format_status_message(self, message):
        name = self.context.get('container_name')
        return message % name

    def handle(self, request, data):
        return True
