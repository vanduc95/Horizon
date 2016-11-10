from horizon import forms
import docker
from openstack_dashboard.dashboards.docker_swarm.docker_service.scale_services import service
from django.utils.translation import ugettext_lazy as _

class ConfigScale(forms.SelfHandlingForm):
    #
    service =forms.ChoiceField(label='Select Service to scale',
                               widget=forms.Select)
    type_config = forms.ChoiceField(label='Type Config',
                                    help_text=_('Choose type of config to scale container'),
                                    widget=forms.Select(attrs={
                                        'class': 'switchable',
                                        'data-slug': 'type_config'}),
                                    choices=[('auto', _('Auto Scale')),
                                             ('user', _('User Scale'))],)

    resource_scale = forms.ChoiceField(label='resource config',
                                       required=False,
                                       widget=forms.Select(attrs={
                                           'class':'switched',
                                           # 'data-slug':'resource_scale',
                                           'data-switch-on':'type_config',
                                           'data-type_config-auto':_('Resource Scale')
                                       }),
                                       choices=[('cpu',_('CPU')),
                                                ('ram',_('RAM'))],
                                       )
    maxCPU = forms.CharField(label='Max CPU to scale',
                             required=False,
                             widget=forms.TextInput(attrs={
                                 'class': 'switched',
                                 # 'data-switch-on': 'resource_scale',
                                 # 'data-resource_scale-cpu': _('Max CPU')
                                 'data-switch-on': 'type_config',
                                 'data-type_config-auto': _('Max CPU')
                             })
                             )

    minCPU = forms.CharField(label='Min CPU to scale',
                             required=False,
                             widget=forms.TextInput(attrs={
                                 'class': 'switched',
                                 # 'data-switch-on': 'resource_scale',
                                 # 'data-resource_scale-cpu': _('MIN CPU')
                                 'data-switch-on': 'type_config',
                                 'data-type_config-auto': _('MIN CPU')
                             }))

    maxRAM = forms.CharField(label='Max RAM to scale',
                             required=False,
                             widget=forms.TextInput(attrs={
                                 'class': 'switched',
                                 # 'data-switch-on': 'resource_scale',
                                 # 'data-resource_scale-ram': _('MAX RAM')
                                 'data-switch-on': 'type_config',
                                 'data-type_config-auto': _('MAX RAM')
                             })
                             )

    minRAM = forms.CharField(label='Min RAM to scale',
                             required=False,
                             widget=forms.TextInput(attrs={
                                 'class': 'switched',
                                 # 'data-switch-on': 'resource_scale',
                                 # 'data-resource_scale-ram': _('MIN RAM')
                                 'data-switch-on': 'type_config',
                                 'data-type_config-auto': _('MIN RAM')
                             })
                             )

    numScale = forms.CharField(label='num replicate to scale',
                                  required=False,
                                  widget=forms.TextInput(attrs={
                                          'class': 'switched',
                                          'data-switch-on': 'type_config',
                                          'data-type_config-user': _('NUM SCALE')
                                }))

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
        request.session['yyy']='test'
        type_config = data['type_config']
        minCPU = data['minCPU']
        maxCPU = data['maxCPU']
        minRAM = data['minRAM']
        maxRAM = data['maxRAM']
        if data['numScale'] !='':
            numScale = int(data['numScale'])
        else:
            numScale = 0
        serviceID = data['service'].encode('ascii','ignore')
        resource = data['resource_scale']
        resetConfig(request,serviceID)
        config = {}
        config_setting = {
            'CPU':{
                'maxCPU':None,
                'minCPU':None
            },
            'RAM':{
                'maxRAM':None,
                'minRAM':None
            },
            'REPLICAS':None,
            'MODE':'',
            'RESOURCE':''
        }
        servicess = True
        if type_config=='auto':
            config_setting['MODE']='auto'
            if(resource=='cpu'):
                config_setting['RESOURCE']='cpu'
                config_setting['CPU']['maxCPU']= maxCPU
                config_setting['CPU']['minCPU']=minCPU
            else:
                config_setting['RESOURCE']='ram'
                config_setting['RAM']['maxRAM']=maxRAM
                config_setting['RAM']['minRAM']=minRAM
        else:
            config_setting['MODE']='user'
            config_setting['REPLICAS']= numScale
            servicess = service.scale(serviceID,numScale)
        config[serviceID]=config_setting

        if (request.session.has_key('config')):
            config_session = request.session['config']
            config_session[serviceID]= config_setting
            request.session['config']=config_session
        else:
            request.session['config']=config

        if servicess :
            return True
        else:
            return False

def resetConfig(request,serviceID):
    if 'config' in request.session:
        if serviceID in request.session['config']:
            request.session['config'][serviceID] = None
    return True