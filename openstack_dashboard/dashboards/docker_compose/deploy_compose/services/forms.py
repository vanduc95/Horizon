from django.utils.translation import ugettext_lazy as _

from horizon import forms



class CreateServiceForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name Service"), required=True)
    command = forms.CharField(max_length=255, label=_("Command"), required=False)
    replicate = forms.CharField(max_length=255, label=_("Replicate"), required=False)

    def handle(self, request, data):

        return True
