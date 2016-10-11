from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables


def get_subnets(network):
    subnet_template = 'docker_management/networks/_render_subnets.html'
    context = {'subnets': network.subnets}
    return template.loader.render_to_string(subnet_template, context)


class ImagesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("Image Id"), truncate=10)
    repository = tables.Column('repository',
                               verbose_name=_("Repository"))
    tag = tables.Column('tag',
                        verbose_name=_("TAG"))
    created = tables.Column('created',
                            verbose_name=_("Created At"))
    size = tables.Column('size',
                         verbose_name=_("Size"))

    def __init__(self, request, *args, **kwargs):
        super(ImagesTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Docker Images"
        name = 'images'
        row_actions = ()


class DockerImagesData:
    def __init__(self, id, repository, tag, create_at, size, host):
        self.id = id
        self.repository = repository
        self.tag = tag
        self.create_at = create_at
        self.size = size
        self.host = host
