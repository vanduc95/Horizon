from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.docker_compose.deploy_compose.services import forms as create_forms
from django.core.urlresolvers import reverse
from horizon import exceptions
from horizon import views
from docker import Client


class CreateService(forms.ModalFormView):
    form_class = create_forms.CreateServiceForm
    form_id = "create_service_form"
    modal_header = _("Create An Service")
    submit_url = reverse_lazy('horizon:docker_compose:deploy_compose:services:create')
    template_name = 'docker_compose/deploy_compose/services/create.html'
    success_url = reverse_lazy("horizon:docker_compose:deploy_compose:index")
    page_title = _("Create An Service")

