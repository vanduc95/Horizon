from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

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
# class DeleteService(tables.DeleteAction):
#     @staticmethod
#     def action_present(count):
#         return ungettext_lazy(
#             u"Delete Docker Host",
#             u"Delete Docker Hosts",
#             count
#         )
#
#     @staticmethod
#     def action_past(count):
#         return ungettext_lazy(
#             u"Deleted Docker Host",
#             u"Deleted Docker Hosts",
#             count
#         )
#
#     # policy_rules = (("network", "delete_network"),)
#
#     def delete(self, request, docker_host_id):
#         docker_host = docker_host_id


class ServiceTable(tables.DataTable):
    id = tables.Column("id")
    name = tables.Column("name", verbose_name="Host Name")
    docker_host_ip = tables.Column("host_ip", verbose_name="Host IP")

    def __init__(self, request, *args, **kwargs):
        super(ServiceTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Services"
        name = 'services'
        # table_actions = (HostFilter, AddService, DeleteService,)
        # row_actions = (UpdateService, DeleteService,)
