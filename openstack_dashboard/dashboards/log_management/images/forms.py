

from horizon import forms

class CreateImage(forms.SelfHandlingForm):

    dockerfile = forms.FileField(label='Docker file',
                                 help_text='choice dockerfile from local',
                                 required=True,
                                 widget=forms.FileInput(),
                                 )
    textChage =forms.CharField(label='Change Content',
                              help_text = 'Change content dockerfile in here',
                              widget = forms.Textarea(),)

    def handle(self,request,data):
        pass