from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Player, Team

@admin.register(Player)
class PlayerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phoneNumber',)}),
    )

admin.site.register(Team)

