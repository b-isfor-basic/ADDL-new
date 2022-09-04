from django.contrib import admin
from .models import Scoreset, GameScore

admin.site.register([Scoreset, GameScore])