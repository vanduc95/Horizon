from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy


from horizon import tables
from docker import Client

class FilterAction(tables.FilterAction):
    name = 'filter_image'

class DeleteImage(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Log",
            u"Delete Logs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Log",
            u"Deleted Logs",
            count
        )

    # policy_rules = (("network", "delete_network"),)

    def delete(self, request, id_image):
        cli = Client(base_url='unix://var/run/docker.sock')
        img_re = None
        imgs = cli.images()
        for img in imgs:
            if img['Id'] == id_image:
                img_re = img
                break
        cli.remove_image(image=img_re, force=True)



class CreateImage(tables.LinkAction):
    name ='createImage'
    verbose_name = _('Create Image')
    url = "horizon:log_management:images:create"
    classes = ('ajax-modal',)
    icon = 'plus'


class Image(tables.DataTable):

    repoTags = tables.Column('repoTags',verbose_name='repoTags',)
    size = tables.Column('size',verbose_name='Size',)
    id = tables.Column('id',verbose_name='Id',truncate=25,)
    parentId = tables.Column('parentId',verbose_name='ParentId',truncate=25,)

    class Meta(object):
        multi_select = True
        name ='image'
        verbose_name= 'Image Docker'
        row_actions = (DeleteImage,)
        table_actions = (DeleteImage,FilterAction,CreateImage,)

class ImageObj:
    def __init__(self,repoTags,size,id,parenId):
        self.id = id
        self.parentId = parenId
        self.repoTags = repoTags
        self.size = size