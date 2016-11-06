from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.docker_swarm.docker_service.service_monitor import forms as create_forms


class ConfigScaleForm(forms.ModalFormView):
    form_class = create_forms.ConfigScale
    form_id = "config_scale_form"
    modal_header = _("Config Auto Scale")
    submit_url = reverse_lazy('horizon:docker_swarm:docker_service:service_monitor:config')
    template_name = 'docker_swarm/docker_service/service_monitor/create.html'
    success_url = reverse_lazy("horizon:docker_swarm:docker_service:index")
    page_title = _("Config Scale")