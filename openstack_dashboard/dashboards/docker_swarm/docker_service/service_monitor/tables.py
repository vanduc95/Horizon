from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from docker import Client
from horizon.utils import filters as filters_horizon
from collections import defaultdict
from horizon import tables


class FilterImageAction(tables.FilterAction):
    name = "myfilter"


class ContainerFixedFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, value, icon):
            return dict(text=text, value=value, icon=icon)

        buttons = [make_dict(_('Running'), 'running', 'fa-play')]
        buttons.append(make_dict(_('Exited'), 'exited', 'fa-stop'))
        buttons.append(make_dict(_('Created'), 'created', 'fa-check-square'))
        return buttons

    def categorize(self, table, containers):

        tenants = defaultdict(list)
        for container in containers:
            # categories = get_container_categories(container)
            # print categories
            # for category in categories:
            # tenants[category].append(container)
            state = get_container_categories(container)
            tenants[state].append(container)
        return tenants


def get_container_categories(container):
    categories = ''
    if (container.state == 'running'):
        categories = 'running'
    elif(container.state == 'exited'):
        categories = 'exited'
    elif(container.state == 'created'):
        categories = 'created'
    return categories


class UpdateRow(tables.Row):
    ajax = True

    def load_cells(self, container=None):
        super(UpdateRow, self).load_cells(container)
        # Tag the row with the image category for client-side filtering.
        container = self.datum
        category = get_container_categories(container)
        self.classes.append('category-' + category)


class ConfigScale(tables.LinkAction):
    name = "config_scale"
    verbose_name = _("Config Scale")
    url = "horizon:docker_swarm:docker_service:service_monitor:config"
    classes = ("ajax-modal",)
    icon = "plus"


class ContainerInServiceTable(tables.DataTable):
    id = tables.Column('id', verbose_name='Container Id')
    image = tables.Column('image', verbose_name='Image')
    command = tables.Column('command', verbose_name='Command')
    created = tables.Column('created', verbose_name='Created', filters=(filters_horizon.parse_isotime,
                                                                        filters_horizon.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    state = tables.Column('state', verbose_name='State')
    name = tables.Column('name', verbose_name='Name')
    host_ip = tables.Column('host_ip', verbose_name='Host_IP')

    class Meta(object):
        row_class = UpdateRow
        name = "container_in_service"
        verbose_name = _("Container In Service")

        table_actions = (ContainerFixedFilter,ConfigScale,)







