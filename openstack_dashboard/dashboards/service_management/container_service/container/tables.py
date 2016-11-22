from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ContainerFilter(tables.FilterAction):
    name = 'container_filter'


def get_names(container):
    subnet_template = 'service_management/container_service/container/_render_names.html'
    context = {'names': container.names}
    return template.loader.render_to_string(subnet_template, context)


def get_ips(container):
    subnet_template = 'service_management/container_service/container/_render_ips.html'
    context = {'ips': container.ips}
    return template.loader.render_to_string(subnet_template, context)


def get_ports(container):
    subnet_template = 'service_management/container_service/container/_render_ports.html'
    context = {'ports': container.ports}
    return template.loader.render_to_string(subnet_template, context)


class ContainerTable(tables.DataTable):
    container_id = tables.Column('id',
                                 verbose_name=_("Container Id"), truncate=10)
    name = tables.Column(get_names,
                         verbose_name=_("Names"))
    state = tables.Column('state',
                          verbose_name=_("State"))
    status = tables.Column('status',
                           verbose_name=_("Status"))
    ip = tables.Column(get_ips,
                       verbose_name=_("Network : IP"))
    port = tables.Column(get_ports,
                         verbose_name=_("Ports Private:Public"))
    image = tables.Column('image',
                          verbose_name=_("Image"))
    service_name = tables.Column('service_name', verbose_name=_("Service"))

    def __init__(self, request, *args, **kwargs):
        super(ContainerTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Docker Container"
        name = 'containers'
        table_actions = (ContainerFilter,)

