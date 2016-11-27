from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from openstack_dashboard.dashboards.service_management.container_service.database import services as database_service
from openstack_dashboard.dashboards.service_management.container_service.service.docker_api import docker_api
from horizon import exceptions
from horizon import tables


# class HostFilter(tables.FilterAction):
#     name = 'container_filter'
#
#
# class AddService(tables.LinkAction):
#     name = "add"
#     verbose_name = _("Add A Docker Host ")
#     url = "horizon:docker_management:docker_monitor:docker_hosts:add"
#     classes = ("ajax-modal",)
#     icon = "plus"
#
#     # policy_rules = (("network", "create_network"),)
#
#     def allowed(self, request, datum=None):
#         return True
#
#
# class UpdateService(tables.LinkAction):
#     name = "update_docker_host"
#     verbose_name = _("Edit Host")
#     url = "horizon:docker_management:docker_monitor:docker_hosts:update"
#     classes = ("ajax-modal",)
#     icon = "pencil"
#     # policy_rules = (("network", "update_network"),)
#
#
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
            u"Delete Service",
            u"Delete Services",
            count
        )

    # policy_rules = (("network", "delete_network"),)

    def delete(self, request, service_id):
        cli = docker_api.connect_docker()
        db_service = database_service.DatabaseService()
        for container in db_service.session.query(database_service.Container). \
                filter(database_service.Container.service_id == service_id):
            cli.stop(container.container_id)
            cli.remove_container(container.container_id)
        for service in db_service.session.query(database_service.Service). \
            filter(database_service.Service.id == int(service_id)):
            db_service.session.delete(service)
            db_service.session.commit()
        db_service.close()


class CreateService(tables.LinkAction):
    name = "create_service"
    verbose_name = _("Create Service")
    url = "horizon:service_management:container_service:service:create"
    classes = ("ajax-modal",)
    icon = "plus"


class ServiceTable(tables.DataTable):
    id = tables.Column("id")
    name = tables.Column("name", verbose_name="Service Name")

    def __init__(self, request, *args, **kwargs):
        super(ServiceTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Services"
        multi_select = True
        name = 'services'
        table_actions = (CreateService, DeleteService,)
        row_actions = (DeleteService,)
