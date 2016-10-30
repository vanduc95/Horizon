from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from docker import Client
import docker


def get_name_images():
    IMAGES = [('', _('Select Image'))]
    cli = Client(base_url='unix://var/run/docker.sock')
    for image in cli.images():
        repo = image['RepoTags']
        repoTags = repo[0]
        IMAGES.append((repoTags, _(repoTags)))

    return IMAGES


class CreateServiceForm(forms.SelfHandlingForm):
    image = forms.ChoiceField(
        label=_('Image Source'),
        choices=get_name_images(),
        required=True,
    )
    name = forms.CharField(max_length=255, label=_("Name Service"), required=True)
    command = forms.CharField(max_length=255, label=_("Command"), required=True)
    replicate = forms.CharField(max_length=255, label=_("Replicate"), required=False)

    def handle(self, request, data):
        try:
            cli = Client(base_url='unix://var/run/docker.sock')
            arr = data['command'].split(' ')
            command = []
            for str in arr:
                command.append(str)
            container_spec = docker.types.ContainerSpec(image=data['image'], command=command)
            task_tmpl = docker.types.TaskTemplate(container_spec)
            if data['replicate'] == '':
                cli.create_service(task_tmpl, name=data['name'])
            else:
                number = int(data['replicate'])
                cli.create_service(task_tmpl, name=data['name'], mode={'Replicated': {'Replicas': number}})

        except Exception:
            exceptions.handle(request, _('Unable to create service.'))
            return False
        return True
