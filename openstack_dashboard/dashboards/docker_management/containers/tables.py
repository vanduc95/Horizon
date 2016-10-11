from collections import defaultdict

from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ContainerFilter(tables.FilterAction):
    name = 'container_filter'


class UpdateRow(tables.Row):
    ajax = True

    def load_cells(self, container=None):
        super(UpdateRow, self).load_cells(container)
        # Tag the row with the image category for client-side filtering.
        container = self.datum
        category = ContainerFixedFilter.get_container_categories(container)
        self.classes.append('category-' + category)


class ContainerFixedFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, value, icon):
            return dict(text=text, value=value, icon=icon)

        buttons = [
            make_dict(_('Running'), 'running', 'fa-play'),
            make_dict(_('Exited'), 'exited', 'fa-stop'),
            make_dict(_('Others'), 'others', 'fa-check-square')
        ]
        return buttons

    def categorize(self, table, containers):

        tenants = defaultdict(list)
        for container in containers:
            state = ContainerFixedFilter.get_container_categories(container)
            tenants[state].append(container)

        return tenants

    @staticmethod
    def get_container_categories(container):
        categories = ''
        if 'running' in container.state:
            categories = 'running'
        elif 'exited' in container.state:
            categories = 'exited'
        else:
            categories = 'others'
        return categories


def get_names(container):
    subnet_template = 'docker_management/containers/_render_names.html'
    context = {'names': container.names}
    return template.loader.render_to_string(subnet_template, context)


def get_ips(container):
    subnet_template = 'docker_management/containers/_render_ips.html'
    context = {'ips': container.ips}
    return template.loader.render_to_string(subnet_template, context)


def get_ports(container):
    subnet_template = 'docker_management/containers/_render_ports.html'
    context = {'ports': container.ports}
    return template.loader.render_to_string(subnet_template, context)


class ContainerTable(tables.DataTable):
    container_id = tables.Column('id',
                                 verbose_name=_("Container Id"),
                                 link="horizon:docker_management:containers:detail",
                                 truncate=10)
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
    host_name = tables.Column('host_name',
                              verbose_name=_("Host Name"))
    image = tables.Column('image',
                          verbose_name=_("Image"))

    def __init__(self, request, *args, **kwargs):
        super(ContainerTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Docker Container"
        name = 'containers'
        table_actions = (ContainerFixedFilter,)
        row_class = UpdateRow
        row_actions = ()


class ContainerData:
    def __init__(self, container_id,host_id, names, state, status, ips, ports, host_name, image):
        self.id = container_id+":"+str(host_id)
        self.names = names
        self.status = status
        self.state = state
        self.image = image
        self.ips = ips
        self.ports = ports
        self.host_name = host_name
