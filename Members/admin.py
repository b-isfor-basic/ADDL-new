from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Player, Team


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("phoneNumber",)}),)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("season", "division", "name")
    list_filter = ("season", "division")
    search_fields = ["name"]
