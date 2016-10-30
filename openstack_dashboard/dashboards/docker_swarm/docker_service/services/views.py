from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.docker_swarm.docker_service.services import forms as create_forms


class CreateService(forms.ModalFormView):
    form_class = create_forms.CreateServiceForm
    form_id = "create_service_form"
    modal_header = _("Create An Service")
    submit_url = reverse_lazy('horizon:docker_swarm:docker_service:services:create')
    template_name = 'docker_swarm/docker_service/services/create.html'
    success_url = reverse_lazy("horizon:docker_swarm:docker_service:index")
    page_title = _("Create An Service")
