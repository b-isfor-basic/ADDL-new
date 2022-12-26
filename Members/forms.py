from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Player


class PlayerCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = Player
        fields = UserCreationForm.Meta.fields + (
            'first_name', 
            'last_name',
            'email', 
            'phoneNumber', 
        )


class PlayerChangeForm(UserChangeForm):
    
    class Meta(UserChangeForm.Meta):
        model = Player
        fields = UserCreationForm.Meta.fields + (
            'first_name', 
            'last_name',
            'email', 
            'phoneNumber', 
        )
        