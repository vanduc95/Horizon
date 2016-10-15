from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.core.urlresolvers import reverse
from horizon import exceptions
from horizon import tables
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database


class HostFilter(tables.FilterAction):
    name = 'container_filter'


class AddDockerHost(tables.LinkAction):
    name = "add"
    verbose_name = _("Add A Docker Host ")
    url = "horizon:docker_management:hosts:add"
    classes = ("ajax-modal",)
    icon = "plus"

    # policy_rules = (("network", "create_network"),)

    def allowed(self, request, datum=None):
        return True


class UpdateDockerHost(tables.LinkAction):
    name = "update_docker_host"
    verbose_name = _("Edit Host")
    url = "horizon:docker_management:hosts:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    # policy_rules = (("network", "update_network"),)


class DeleteDockerHost(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Docker Host",
            u"Delete Docker Hosts",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Docker Host",
            u"Deleted Docker Hosts",
            count
        )

    # policy_rules = (("network", "delete_network"),)

    def delete(self, request, docker_host_id):
        docker_host = docker_host_id
        try:
            db_service = docker_host_database.DataService()
            docker_host_existed = db_service.session.query(docker_host_database.DockerHost). \
                filter_by(id=docker_host_id).first()
            db_service.session.delete(docker_host_existed)
            db_service.session.commit()
            msg = _('Docker Host is Deleted ! %s')
        except Exception:
            msg = (_('Failed to remove docker host "%(host_name)s"') %
                   {"host_name": docker_host_id})
            redirect = reverse('horizon:docker_management:networks:index')
            exceptions.handle(request, msg, redirect=redirect)


class HostTable(tables.DataTable):
    id = tables.Column("id")
    name = tables.Column("name", verbose_name="Host Name")
    docker_host_ip = tables.Column("host_ip", verbose_name="Host IP")

    def __init__(self, request, *args, **kwargs):
        super(HostTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Docker Hosts"
        name = 'docker_hosts'
        table_actions = (HostFilter, AddDockerHost, DeleteDockerHost,)
        row_actions = (UpdateDockerHost, DeleteDockerHost,)
