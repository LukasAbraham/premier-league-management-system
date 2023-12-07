from django.contrib import admin
from .models import Match, GoalEvent, Result

admin.site.register(Match)
admin.site.register(GoalEvent)
admin.site.register(Result)