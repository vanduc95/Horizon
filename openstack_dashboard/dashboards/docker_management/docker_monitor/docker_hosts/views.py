# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon.utils import memoized
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from openstack_dashboard.dashboards.docker_management.docker_monitor.docker_hosts\
    import forms as docker_forms


class AddDockerHostView(forms.ModalFormView):
    form_class = docker_forms.AddDockerHostForm
    form_id = "add_docker_host_form"
    modal_header = _("Add  A Docker Host")
    submit_label = _("Add Docker Host")
    submit_url = reverse_lazy('horizon:docker_management:docker_monitor:docker_hosts:add')
    template_name = 'docker_management/docker_monitor/docker_hosts/create.html'
    success_url = reverse_lazy('horizon:docker_management:docker_monitor:index')
    page_title = _("Add A Docker Host")

    def get_initial(self):
        initial = {}
        return initial


class DockerHostUpdateView(forms.ModalFormView):
    context_object_name = 'docker_host'
    form_class = docker_forms.UpdateDockerHostForm
    form_id = "update_docker_host_form"
    modal_header = _("Edit Docker Host")
    submit_label = _("Save Changes")
    submit_url = 'horizon:docker_management:docker_monitor:docker_hosts:update'
    success_url = reverse_lazy('horizon:docker_management:docker_monitor:index')
    template_name = 'docker_management/docker_monitor/docker_hosts/update.html'
    page_title = _("Update Docker Host")

    def get_context_data(self, **kwargs):
        context = super(DockerHostUpdateView, self).get_context_data(**kwargs)
        args = (self.kwargs['host_id'],)
        context["host_id"] = self.kwargs['host_id']
        context["submit_url"] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        host_id = self.kwargs['host_id']
        try:
            db_service = docker_host_database.DataService()
            docker_host_existed = db_service.session.query(docker_host_database.DockerHost). \
                filter_by(id=host_id).first()
            return docker_host_existed
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve docker host details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        docker_host = self._get_object()
        return {'host_id': docker_host.id,
                'host_name': docker_host.host_name,
                'host_ip': docker_host.host_url,
                }
