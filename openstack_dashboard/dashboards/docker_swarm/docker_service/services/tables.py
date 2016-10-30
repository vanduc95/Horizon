from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from docker import Client
from horizon.utils import filters as filters_horizon
from horizon import tables


class FilterImageAction(tables.FilterAction):
    name = "myfilter"


class CreateService(tables.LinkAction):
    name = "create_service"
    verbose_name = _("Create Service")
    url = "horizon:docker_swarm:docker_service:services:create"
    classes = ("ajax-modal",)
    icon = "plus"


class DeleteService(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Service",
            u"Delete Services",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Service",
            u"Deleted Services",
            count
        )

    def delete(self, request, obj_id):
        cli = Client(base_url='unix://var/run/docker.sock')
        for service in cli.services():
            if(service['ID'] == obj_id):
                cli.remove_service(obj_id)
                break;


class DockerServiceTable(tables.DataTable):
    id = tables.Column('id', verbose_name='Service ID')
    name = tables.Column('name', verbose_name='Name')
    replicate = tables.Column('replicate', verbose_name='Replicate')

    def __init__(self, request, *args, **kwargs):
        super(DockerServiceTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = "docker_service"
        verbose_name = _("Docker Service")
        table_actions = (FilterImageAction, CreateService, DeleteService, )
