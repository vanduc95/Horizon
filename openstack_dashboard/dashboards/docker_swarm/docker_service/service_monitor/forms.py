from horizon import forms


class ConfigScale(forms.SelfHandlingForm):
    TYPE_CHOICE = [['autoScale', 'Auto'],
                   ['userScale', 'User']]

    type_config = forms.ChoiceField(label='Type Config',
                                    required=False,
                                    widget=forms.Select(attrs={
                                        'class': 'switchable',
                                        'data-slug': 'source'}),
                                    choices=TYPE_CHOICE, )
    maxCPU = forms.CharField(label='Max CPU to scale',
                             widget=forms.Select(attrs={'class': 'auto-scale'}))
    minCPU = forms.CharField(label='Min CPU to scale',
                             widget=forms.Select(attrs={'class': 'auto-scale'}))
    maxRAM = forms.CharField(label='Max RAM to scale',
                             widget=forms.Select(attrs={'class': 'auto-scale'}))
    minRAM = forms.CharField(label='Min RAM to scale',
                             widget=forms.Select(attrs={'class': 'auto-scale'}))

    numScale = forms.CharField(label='num replicate to scale',
                               widget=forms.Select(attrs={'class': 'user-scale'}))

    def handle(self, request, data):
        pass
