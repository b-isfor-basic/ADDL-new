from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Player, Team


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("phoneNumber",)}),)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_select_related = ("season", "division")
    list_display = ("season", "division", "name")
    list_filter = ("season", "division")
    search_fields = ["name"]

    def name(self, obj):
        plyrs = obj.players.all()
        return plyrs[0].last_name + "/" + plyrs[1].last_name
