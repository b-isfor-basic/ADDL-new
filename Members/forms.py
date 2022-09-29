from django import forms
from django.conf import settings

import djhacker
from dal import autocomplete

user = settings.AUTH_USER_MODEL

djhacker.formfield(
    user.full_name,
    forms.ModelChoiceField,
    widget=autocomplete.ModelSelect2(url='player-autocomplete')
)