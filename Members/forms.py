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
        fieldsets = [
            ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phoneNumber')}), 
            ('Account Info', {'fields': ('username', 'password1', 'password2')})
        ]


class PlayerChangeForm(UserChangeForm):
    
    class Meta(UserChangeForm.Meta):
        model = Player
        fields = UserCreationForm.Meta.fields + (
            'first_name', 
            'last_name',
            'email', 
            'phoneNumber', 
        )
        fieldsets = [
            ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phoneNumber')}), 
            ('Account Info', {'fields': ('username', 'password1', 'password2')})
        ]
        