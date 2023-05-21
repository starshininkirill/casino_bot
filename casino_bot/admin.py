from django.contrib import admin
from .models import *

admin.register(Stages)
admin.register(User)
admin.register(CubeGame)


@admin.register(User)
class User_admin(admin.ModelAdmin):
    list_display = ('id', 'username', 'tg_uid', 'balance', 'stage', 'games_count')
    list_display_links = ('id', 'username', )
    list_editable = ('balance', 'stage', 'games_count')
    list_filter = ('tg_uid', )


@admin.register(Stages)
class Stages_admin(admin.ModelAdmin):
    list_display = ('id', 'current_stage', 'next_stage')
    list_display_links = ('id',)
    list_editable = ('next_stage', 'current_stage',)


@admin.register(CubeGame)
class CubeGame_admin(admin.ModelAdmin):
    list_display = ('id', 'bet', 'position', )
    list_display_links = ('id', )
