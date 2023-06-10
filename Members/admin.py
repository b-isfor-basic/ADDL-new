from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Player, Team


@admin.register(Player)
class PlayerAdmin(UserAdmin, admin.ModelAdmin):
    fieldsets = [UserAdmin.fieldsets[0]]
    fieldsets += [
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phoneNumber",
                )
            },
        ),
    ]
    fieldsets += UserAdmin.fieldsets[2:]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_select_related = ("season", "division")
    list_display = ("season", "division", "name")
    list_filter = ("season", "division")
    search_fields = ["name"]

    @admin.display(description="Name")
    def name(self, obj):
        plyrs = obj.players.all()
        return plyrs[0].last_name + "/" + plyrs[1].last_name
