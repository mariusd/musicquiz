from musicquiz.quiz.models import Artist
from musicquiz.quiz.models import Track
from musicquiz.quiz.models import Question
from musicquiz.quiz.models import Game
from django.contrib import admin

class TrackAdmin(admin.ModelAdmin):
    list_display = ('artist', 'title', 'youtube_code', 'youtube_duration')
   
admin.site.register(Artist)
admin.site.register(Track, TrackAdmin)
admin.site.register(Question)
admin.site.register(Game)
