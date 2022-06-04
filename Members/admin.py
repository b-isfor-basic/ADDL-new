from django.contrib import admin
from .models import Profile, Team

admin.site.register(Profile)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['display_players']
