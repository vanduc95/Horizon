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
            u"Delete Image",
            u"Delete Image",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Image",
            u"Deleted Image",
            count
        )

    # policy_rules = (("network", "delete_network"),)

    def delete(self, request, id_image,**kwargs):
        arr = id_image.split('||')
        host = arr[1]
        # print(host)
        base_url = 'tcp://'+host
        print(arr[0]+'  ---  '+base_url)
        cli = Client(base_url='tcp://'+host)
        img_re = None
        imgs = cli.images()
        for img in imgs:
            if img['Id'] == arr[0]:
                img_re = img
                break
        cli.remove_image(image=img_re, force=True)



class CreateImage(tables.LinkAction):
    name ='createImage'
    verbose_name = _('Create Image')
    url = "horizon:log_management:images:create"
    classes = ('ajax-modal',)
    icon = 'plus'

class AddDockerHost(tables.LinkAction):
    name ='addDocker'
    verbose_name = _('Add Docker Host')
    url = "horizon:log_management:images:add"
    classes = ('ajax-modal',)
    icon = 'plus'


class Image(tables.DataTable):

    repoTags = tables.Column('repoTags',verbose_name='repoTags',)
    size = tables.Column('size',verbose_name='Size',)
    id = tables.Column('id',verbose_name='Id',truncate=25,)
    parentId = tables.Column('parentId',verbose_name='ParentId',truncate=25,)
    host_url = tables.Column('hostUrl',verbose_name='Host URL',)
    host_port = tables.Column('hostPort',verbose_name='hostPort',)

    class Meta(object):
        multi_select = True
        name ='image'
        verbose_name= 'Image Docker'
        row_actions = (DeleteImage,)
        table_actions = (DeleteImage,FilterAction,CreateImage,AddDockerHost,)

class ImageObj:
    def __init__(self,repoTags,size,id,parenId,host_url,host_port):
        self.id = id+'||'+host_url+':'+host_port
        self.parentId = parenId
        self.repoTags = repoTags
        self.size = size
        self.hostUrl=host_url
        self.hostPort = host_port