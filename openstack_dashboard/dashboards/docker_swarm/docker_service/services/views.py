from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from openstack_dashboard.dashboards.docker_swarm.docker_service.services import forms as create_forms
from django.core.urlresolvers import reverse
from horizon import exceptions
from horizon import views
from docker import Client

INDEX_URL = "horizon:docker_swarm:docker_service:index"


class CreateService(forms.ModalFormView):
    form_class = create_forms.CreateServiceForm
    form_id = "create_service_form"
    modal_header = _("Create An Service")
    submit_url = reverse_lazy('horizon:docker_swarm:docker_service:services:create')
    template_name = 'docker_swarm/docker_service/services/create.html'
    success_url = reverse_lazy("horizon:docker_swarm:docker_service:index")
    page_title = _("Create An Service")


class DetailServiceView(views.APIView):
    template_name = 'docker_swarm/docker_service/services/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailServiceView, self).get_context_data(**kwargs)
        try:
            service_id = self.kwargs['service_id']

            cli = Client(base_url='unix://var/run/docker.sock')

            inspect_service = cli.inspect_service(service_id)
            image = inspect_service['Spec']['TaskTemplate']['ContainerSpec']['Image']
            name = inspect_service['Spec']['Name']
            replicate = inspect_service['Spec']['Mode']['Replicated']['Replicas']

            service = Service(service_id, image, name, replicate)
            context['service'] = service
            return context

        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve service details.'),
                              redirect=reverse(INDEX_URL))


class Service:
    def __init__(self, service_id, image, name, replicate):
        self.id = service_id
        self.image = image
        self.name = name
        self.replicate = replicate
