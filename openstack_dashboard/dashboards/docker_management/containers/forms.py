# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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

"""
"""
import django.core.urlresolvers
from django.utils.translation import ugettext_lazy as _

# from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from docker import Client


class CreateContainerForm(forms.SelfHandlingForm):
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
        help_text=_("Local image"),
        widget=forms.Select(attrs={
            'class': 'switched',
            'data-switch-on': 'image_source',
            'data-image_source-local': _('Image Local')
        })
    )

    image_repository = forms.CharField(
        max_length=255,
        label=_("Repository Image"),
        help_text=_("Repository image"),
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'image_source',
            'data-image_source-repository': _('Image Repo'),
            'placeholder': 'Type image name in repository'
        }))

    def __init__(self, request, *args, **kwargs):
        super(CreateContainerForm, self).__init__(request, *args, **kwargs)
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
                images_choice.append((image['Id']+":"+str(host.id), CreateContainerForm.get_images_name(image['RepoTags'])))
        self.fields['image_local'].choices = images_choice

    @staticmethod
    def get_images_name(image_names):
        image_join_names = ''
        for name in image_names:
            image_join_names += name
        return image_join_names

    def clean(self):
        cleaned_data = super(CreateContainerForm, self).clean()
        return cleaned_data

    def handle(self, request, data):

        messages.success(request,
                         _('New container has been created') % data['container_name'])
        return True

    def get_success_url(self):
        return django.core.urlresolvers.reverse("horizon:docker_management:containers:index")

    def get_failure_url(self):
        return django.core.urlresolvers.reverse("horizon:docker_management:containers:index")
