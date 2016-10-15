from django import template
from horizon import tables
from docker import Client
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from openstack_dashboard.dashboards.docker_management.database import database as docker_host_database
from django.core.urlresolvers import reverse
from horizon import exceptions


class CreateNetworkAction(tables.LinkAction):
    name = "add"
    verbose_name = _("Create Network ")
    url = "horizon:docker_management:networks:create"
    classes = ("ajax-modal",)
    icon = "plus"

    # policy_rules = (("network", "create_network"),)

    def allowed(self, request, datum=None):
        return True


class NetworkFilter(tables.FilterAction):
    name = 'container_filter'


class DeleteDockerHost(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Network",
            u"Delete Networks",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Network",
            u"Deleted Networks",
            count
        )

    # policy_rules = (("network", "delete_network"),)

    def delete(self, request, networks_and_host_id):
        network_host_id = networks_and_host_id.split(':')
        network_id = network_host_id[0]
        host_id = network_host_id[1]
        try:
            db_service = docker_host_database.DataService()
            docker_host = db_service.session.query(docker_host_database.DockerHost). \
                filter_by(id=host_id).first()
            docker_cli = Client(base_url='tcp://' + docker_host.host_url + ':2376')
            docker_cli.remove_network(network_id)
            msg = _('Docker Host is Deleted ! %s')
        except Exception as e:
            msg = _('Failed to delete network: '
                    ' %(reason)s')% {"reason": e}
            redirect = reverse('horizon:docker_management:networks:index')

            exceptions.handle(request,
                              msg,redirect=redirect)


def get_subnets(network):
    subnet_template = 'docker_management/networks/_render_subnets.html'
    context = {'subnets': network.subnets}
    return template.loader.render_to_string(subnet_template, context)


def get_id(network):
    return network.id.split(":")[0]


class NetworksTable(tables.DataTable):
    container_id = tables.Column(get_id,
                                 verbose_name=_("Network Id"), truncate=20)
    name = tables.Column('name',
                         verbose_name=_("Name"))
    driver = tables.Column('driver',
                           verbose_name=_("Driver"))
    subnets = tables.Column(get_subnets,
                            verbose_name=_("Subnets"))
    scope = tables.Column('scope',
                          verbose_name=_("Scope"))
    host = tables.Column('host',
                         verbose_name=_("Host"))

    def __init__(self, request, *args, **kwargs):
        super(NetworksTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Docker Networks"
        name = 'networks'
        row_actions = (DeleteDockerHost,)
        table_actions = (CreateNetworkAction, NetworkFilter, DeleteDockerHost)


class DockerNetworkData:
    def __init__(self, network_id, host_id, name, driver, subnets, scope, host):
        self.id = network_id + ":" + host_id
        self.name = name
        self.driver = driver
        self.subnets = subnets
        self.scope = scope
        self.host = host


class DockerSubnetData:
    def __init__(self, net_mask, gateway):
        self.net_mask = net_mask
        self.gateway = gateway
