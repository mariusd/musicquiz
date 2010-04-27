from musicquiz.quiz.models import Song
from django.contrib import admin

class SongAdmin(admin.ModelAdmin):
    list_display = ('artist', 'title', 'youtube_code')
    
admin.site.register(Song, SongAdmin)