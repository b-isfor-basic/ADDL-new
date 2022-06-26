from django import forms

from .models import Establishment, Division

class DivisionForm(forms.ModelForm):

    class Meta:
        model = Division
        fields = (
            'matchNight',
            'playerFee',
            'capacity',
            'divisionManager',
            'season'
        )


class EstablishmentForm(forms.ModelForm):
    
    class Meta:
        model = Establishment
        fields = (
            'number',
            'name',
            'streetLine1',
            'streetLine2',
            'city',
            'state',
            'zipCode',
            'generalManager',
            'managerEmail',
            'managerPhone',
        )