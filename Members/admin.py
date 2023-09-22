from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Player, Team, Registration


@admin.register(Player)
class PlayerAdmin(UserAdmin, admin.ModelAdmin):
    fieldsets = [UserAdmin.fieldsets[0]]
    fieldsets += [
        (
            "Personal info",
            {
                "fields": (
                    ("first_name", "last_name"),
                    "email",
                    "phoneNumber",
                )
            },
        ),
    ]
    fieldsets += UserAdmin.fieldsets[2:]
    

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_filter = ["season", ("division", admin.RelatedOnlyFieldListFilter)]
    list_display = ("team", "season", "division")
    fieldsets = [
        ("Season", {"fields": ["season", "division"]}),
        ("Teams", {"fields": ["team"]}),
    ]


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 5


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_filter = ["season", ("division", admin.RelatedOnlyFieldListFilter)]
    filter_horizontal = ["players"]
    inlines = [RegistrationInline]

    @admin.display(description="Name")
    def name(self, obj):
        plyrs = obj.players.all()
        return plyrs[0].last_name + "/" + plyrs[1].last_name
    
    