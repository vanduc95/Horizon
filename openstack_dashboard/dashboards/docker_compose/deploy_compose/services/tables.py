from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from docker import Client
from horizon import forms
from horizon.utils import filters as filters_horizon
from horizon import tables


class CreateService(tables.LinkAction):
    name = "create_service"
    verbose_name = _("Create Service")
    url = "horizon:docker_compose:deploy_compose:services:create"
    classes = ("ajax-modal",)
    icon = "plus"

class ServiceTable(tables.DataTable):
    service_id = tables.Column('id', verbose_name='Service ID', truncate=15)
    image = tables.Column('image', verbose_name='Image')
    name = tables.Column('name', verbose_name='Name')
    replicate = tables.Column('replicate', verbose_name='Replicate')

    def __init__(self, request, *args, **kwargs):
        super(ServiceTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = "services"
        verbose_name = _("Services")
        table_actions = (CreateService,)
