

from horizon import forms
from openstack_dashboard.dashboards.log_management.images import models as project_model
from horizon import messages
from django.utils.translation import ugettext_lazy as _

class CreateImage(forms.SelfHandlingForm):

    dockerfile = forms.FileField(label='Docker file',
                                 help_text='choice docker host',
                                 required=True,
                                 widget=forms.FileInput(),
                                 )
    textChage =forms.CharField(label='Change Content',
                              help_text = 'Change content dockerfile in here',
                              widget = forms.Textarea(),)

    def handle(self,request,data):
        pass


class AddDockerHost(forms.SelfHandlingForm):

    hostUrl = forms.CharField(max_length= 30,
                                label='Host Url',
                                 help_text='choice docker',
                                 required=True,
                                 )
    port =forms.CharField(max_length=10,
                          label='Port',
                            help_text = 'Enter port of Docker Host',)

    def handle(self,request,data):
        url = data['hostUrl']
        port = data['port']
        session = project_model.create_session()
        host = project_model.DockerHost(host_url=url,host_port=port)
        for host_url,host_port in session.query(project_model.DockerHost.host_url,project_model.DockerHost.host_port):
            if ((host_url==url)and(host_port==port)):
                messages.error(request, 'Docker host already exist', fail_silently=False)
                return False
        session.add(host)
        session.commit()
        session.close()
        messages.success(request, 'successfully', fail_silently=False)
        return True