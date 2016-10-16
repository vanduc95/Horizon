

from horizon import forms

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
        pass