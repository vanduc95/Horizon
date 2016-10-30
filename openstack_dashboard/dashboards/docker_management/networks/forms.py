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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database


class AddNetworkForm(forms.SelfHandlingForm):
    host_id = forms.ChoiceField(label=_("Host"))
    host_ip = forms.IPField(
        label=_("Host IP"),
        required=True,
        initial="",
        # version=forms.IPv4 | forms.IPv6,
        version=forms.IPv4,
        mask=False
    )

    def __init__(self, request, *args, **kwargs):
        super(AddNetworkForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        cleaned_data = super(AddNetworkForm, self).clean()
        db_service = docker_host_database.DataService()
        docker_host_existed = db_service.session.query(docker_host_database.DockerHost). \
            filter_by(host_url=cleaned_data.get('host_ip')).first()
        if docker_host_existed is not None:
            msg = _('This Host IP is duplicated!')
            raise forms.ValidationError(msg)
        return cleaned_data

    def _add_new_docker_host(self, request, data):
        try:
            db_service = docker_host_database.DataService()
            new_docker_host = docker_host_database.DockerHost(
                host_name=data['host_name'], host_url=data['host_ip'])
            db_service.session.add(new_docker_host)
            db_service.session.commit()
            return True
        except Exception as e:
            msg = (_('Failed to add new docker host "%(host_name)s": %(reason)s') %
                   {"host_name": data['host_name'], "reason": e})
            redirect = self.get_failure_url()
            exceptions.handle(request, msg, redirect=redirect)
            return False

    def handle(self, request, data):
        is_success_to_add_docker_host = self._add_new_docker_host(request, data)
        if not is_success_to_add_docker_host:
            return False
        messages.success(request,
                         _('Docker Host "%s" was successfully added.') % data['host_name'])
        return True

    def get_success_url(self):
        return reverse("horizon:docker_management:hosts:index")

    def get_failure_url(self):
        return reverse("horizon:docker_management:hosts:index")


class UpdateDockerHostForm(forms.SelfHandlingForm):
    host_id = forms.CharField(label=_("ID"),
                              widget=forms.TextInput(
                                  attrs={'readonly': 'readonly'}))
    host_name = forms.CharField(max_length=255,
                                label=_("Host Name"),
                                required=True)
    host_ip = forms.IPField(
        label=_("Host IP"),
        required=True,
        initial="",
        help_text=_("IP of Docker Host which you want to add to system, only support IP v4"),
        # version=forms.IPv4 | forms.IPv6,
        version=forms.IPv4,
        mask=False
    )

    def __init__(self, request, *args, **kwargs):
        super(UpdateDockerHostForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        cleaned_data = super(UpdateDockerHostForm, self).clean()
        db_service = docker_host_database.DataService()
        docker_host_existed = db_service.session.query(docker_host_database.DockerHost). \
            filter_by(host_url=cleaned_data.get('host_ip')).first()
        if (docker_host_existed is not None) and str(docker_host_existed.id) != cleaned_data.get('host_id'):
            msg = _('This Host IP is duplicated!')
            raise forms.ValidationError(msg)
        return cleaned_data

    def _update_docker_host(self, request, data):
        try:
            db_service = docker_host_database.DataService()
            # new_docker_host = docker_host_database.DockerHost(
            #     host_name=data['host_name'], host_url=data['host_ip'])
            db_service.session.query(docker_host_database.DockerHost). \
                filter(docker_host_database.DockerHost.id == data['host_id']). \
                update({'host_name': data['host_name'], 'host_url': data['host_ip']})
            db_service.session.commit()
            return True
        except Exception as e:
            msg = (_('Failed to update host "%(host_id)s": %(reason)s') %
                   {"host_id": data['host_id'], "reason": e})
            redirect = self.get_failure_url()
            exceptions.handle(request, msg, redirect=redirect)
            return False

    def handle(self, request, data):
        is_success_to_update_docker_host = self._update_docker_host(request, data)
        if not is_success_to_update_docker_host:
            return False
        messages.success(request,
                         _('Docker Host "%s" was successfully updated.') % data['host_name'])
        return True

    def get_success_url(self):
        return reverse("horizon:docker_management:hosts:index")

    def get_failure_url(self):
        return reverse("horizon:docker_management:hosts:index")
