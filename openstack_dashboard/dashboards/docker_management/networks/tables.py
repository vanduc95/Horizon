from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables


def get_subnets(network):
    subnet_template = 'docker_management/networks/_render_subnets.html'
    context = {'subnets': network.subnets}
    return template.loader.render_to_string(subnet_template, context)


class NetworksTable(tables.DataTable):
    container_id = tables.Column('id',
                                 verbose_name=_("Network Id"), truncate=40)
    name = tables.Column('name',
                         verbose_name=_("Names"))
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
        row_actions = ()


class DockerNetworkData:
    def __init__(self, network_id, name, driver, subnets, scope, host):
        self.id = network_id
        self.name = name,
        self.driver = driver
        self.subnets = subnets
        self.scope = scope
        self.host = host


class DockerSubnetData:
    def __init__(self,net_mask,gateway):
        self.net_mask = net_mask
        self.gateway = gateway
