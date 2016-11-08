from horizon import forms
# from django.contrib import sessions
import docker
from openstack_dashboard.dashboards.docker_swarm.docker_service.scale_services import service
from django.utils.translation import ugettext_lazy as _

class ConfigScale(forms.SelfHandlingForm):

    TYPE_CHOICE = [['autoScale','Auto Scale'],
                   ['userScale','User Scale']]

    service =forms.ChoiceField(label='Select Service to scale',
                               widget=forms.Select)
    type_config = forms.ChoiceField(label='Type Config',
                                    required=False,
                                    widget=forms.Select(attrs={
                                        'class': 'switchable',
                                        'data-slug': 'image_source'}),
                                    choices=TYPE_CHOICE,)

    maxCPU = forms.CharField(label='Max CPU to scale',
                             # widget=forms.TextInput(attrs={
                             #     'class': 'switched',
                             #     'data-switch-on': 'image_source',
                             #     'data-image_source-autoScale': _('Image Local')
                             # })
                             )

    minCPU = forms.CharField(label='Min CPU to scale',)
                             # widget=forms.TextInput(attrs={
                             #     'class': 'switched',
                             #     'data-switch-on': 'image_source',
                             #     'data-image_source-autoScale': _('Image Local')
                             # }))

    maxRAM = forms.CharField(label='Max RAM to scale',)
                             # widget=forms.TextInput(attrs={
                             #     'class': 'switched',
                             #     'data-switch-on': 'image_source',
                             #     'data-image_source-autoScale': _('Image Local')
                             # })
                             # )

    minRAM = forms.CharField(label='Min RAM to scale',)
                             # widget=forms.TextInput(attrs={
                             #     'class': 'switched',
                             #     'data-switch-on': 'image_source',
                             #     'data-image_source-autoScale': _('Image Local')
                             # })
                             # )

    numScale = forms.DecimalField(label='num replicate to scale',
                                  # image_repository=forms.CharField(
                                  #     max_length=255,
                                  #     label=_("Repository Image"),
                                  #     help_text=_("Repository image"),
                                  #     widget=forms.TextInput(attrs={
                                  #         'class': 'switched',
                                  #         'data-switch-on': 'image_source',
                                  #         'data-image_source-userScale': _('Image Repo'),
                                  #         'placeholder': 'Type image name in repository'
                                  #     }))
                                  )

    def __init__(self,request,*args,**kwargs):
        super(ConfigScale,self).__init__(self,*args,**kwargs)
        cli = docker.Client(base_url='unix://var/run/docker.sock')
        services = cli.services()
        services_name = []
        for service in services:
            name =[]
            name.append(service['ID'])
            name.append(service['Spec']['Name'])
            services_name.append(name)

        self.fields['service'].choices = services_name


    def handle(self,request,data):
        type_config = data['type_config']
        minCPU = data['minCPU']
        maxCPU = data['maxCPU']
        minRAM = data['minRAM']
        maxRAM = data['maxRAM']
        numScale = data['numScale']
        serviceID = data['service']
        # print serviceID,numScale,type(serviceID),type(numScale),type(serviceID.encode('ascii','ignore'),int(numScale)
        #
        if type_config=='autoScale':
            request.session['minCPU']=minCPU
            request.session['maxCPU']=maxCPU
            request.session['minRAM']=minRAM
            request.session['maxRAM']=maxRAM
            request.session['numScale']=''
        else:
            servicess = service.scale(serviceID.encode('ascii','ignore'),int(numScale))
            print servicess
        return True