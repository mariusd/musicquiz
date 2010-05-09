from django.db import models
from django.db import IntegrityError
from django.conf import settings
from utility import extract_youtube_code
import gdata.youtube
import gdata.youtube.service
import pylast
import random
import urllib

EPSILON = 1e-9

class Error(Exception):
    """Base class for exceptions in this module."""
    pass
    
class QuizModelError(Error):
    
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
        
# Create your models here.

class Artist(models.Model):
    """Artist model class."""
    
    name = models.CharField(max_length=128)
    
    def fetch_similar(self):
        """Fetch similar artists from last.fm databases."""
        pass
    
    def fetch_tracks(self):
        """Fetch the titles of artist's tracks from last.fm."""
        pass
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    
class Track(models.Model):
    """Track model class."""
    
    artist = models.ForeignKey(Artist)
    title = models.CharField(max_length=256)
    
    youtube_code = models.CharField(max_length=20, null=True, blank=True)
    youtube_duration = models.IntegerField(null=True, blank=True)
    
    @staticmethod
    def pick_random(exclude=[]):
        """Pick a random track which is not in the exclude list.
        
        Returned track is guaranteed to have youtube code and duration.
        """
        exclude_pks = [track.pk for track in exclude]
        try:
            track = random.choice(Track.objects.exclude(pk__in=exclude_pks))
        except IndexError, e:
            raise ValueError('could not pick any track')
        else:
            if not track.has_youtube_info():
                track.update_youtube_info()
            if track.has_youtube_info():
                return track
            else:
                return Track.pick_random(exclude=exclude + [track])
    
    def has_youtube_info(self):
        """Check if track has all required info about its youtube video."""
        youtube_info = [self.youtube_code, self.youtube_duration]
        return all(field is not None for field in youtube_info)
        
    def update_youtube_info(self):
        """Find youtube video for the track and update youtube info fields."""
        service = gdata.youtube.service.YouTubeService()
        query = gdata.youtube.service.YouTubeVideoQuery()
        query_string = u'%s %s' % (self.artist, self.title)
        query.vq = query_string.encode('utf-8')
        feed = service.YouTubeQuery(query)
        if len(feed.entry) > 0:
            entry = feed.entry[0]
            url = entry.GetSwfUrl()
            if url:
                self.youtube_code = extract_youtube_code(url)
                self.youtube_duration = entry.media.duration.seconds
                self.save()
        else:
            # No youtube video was found, raise an exception?
            pass
            
    def fetch_similar(self, limit=None):
        """Fetch a list or similar tracks and save them in the database.
        
        Returns the count of newly added similar tracks.
        """
        if limit is not None and limit < 0:
            raise ValueError('limit must be a positive integer')
        network = pylast.get_lastfm_network(api_key=settings.LASTFM_API_KEY)
        lastfm_track = network.get_track(unicode(self.artist), self.title)
        similar = lastfm_track.get_similar()
        new_songs = 0
        if limit is not None:
            similar = similar[:limit]
        for similar_track in similar:
            artist_name = similar_track.item.artist.name
            title = similar_track.item.title
            artist, _ = Artist.objects.get_or_create(name=artist_name)      
            result = Track.objects.get_or_create(artist=artist, title=title)
            if result[1]:
                new_songs += 1
        return new_songs
    
    def __unicode__(self):
        return u'%s \u2013 %s' % (self.artist, self.title)
    
    
class Question(models.Model):
    """Quiz question model class."""

    QUESTION_STATES = (
        ('NOANSWER', 'Not answered'),
        ('ANSWERED', 'Submitted'),
        ('TIMEOUT', 'Timeout'),
        ('SKIPPED', 'Skipped'),
        ('REPORTED', 'Reported as bad'),
    )
    
    game = models.ForeignKey('Game', related_name='questions')
    number = models.IntegerField()
    state = models.CharField(max_length=8,
                choices=QUESTION_STATES, default='NOANSWER')
    correct_answer = models.ForeignKey(Track, related_name='in_question')
    
    points = models.FloatField(null=True, blank=True)
    given_answer = models.ForeignKey(Track, null=True, blank=True)
    remaining_time = models.FloatField(null=True, blank=True)
    
    def is_answered(self):
        return self.state != 'NOANSWER'
        
    def answered_correctly(self):
        if self.is_timeout():
            return False
        return self.correct_answer == self.given_answer
        
    def make_guess(self, guess):
        self.remaining_time = guess['remaining_time']
        if 'answer' in guess.keys():
            given_answer = Track.objects.get(id=guess['answer'])
            self.given_answer = given_answer
        if abs(self.remaining_time) > EPSILON:
            self.state = 'ANSWERED'
        else:
            self.state = 'TIMEOUT'
        self.calculate_points()
        self.save()
        
    def calculate_points(self):
        if self.answered_correctly():
            self.points = self.remaining_time
        elif self.state == 'ANSWERED' and not self.answered_correctly():
            self.points = -10
        else:
            self.points = 0
        self.save()
        return self.points
        
    def skip_question(self):
        self.given_answer = None
        self.remaining_time = None
        self.state = 'SKIPPED'
        self.calculate_points()
        self.save()
        
    def is_timeout(self):
        return self.state == 'TIMEOUT'
        
    def get_choices(self, count=8):
        """Return a list of randomly selected possible answers.
        
        Correct answer is always one of the possible choices, but
        other tracks in the list are very likely to be different
        each time this method gets called.
        """
        if count < 1:
            raise ValueError('there must be at least one answer')
        query = Track.objects.exclude(pk__in=[self.correct_answer.pk])
        choices = random.sample(query, count - 1) + [self.correct_answer]
        random.shuffle(choices)
        return choices

    def __unicode__(self):
        return u'%s %s. %s' % (self.game, self.number, self.correct_answer)
        
        
class Game(models.Model):
    """Quiz game model class."""
    
    quiz_length = models.IntegerField()
    date_started = models.DateTimeField(auto_now_add=True)
    
    def next_question(self):
        """Create and return next question for the game."""
        if self.is_game_finished():
            raise QuizModelError('game is already over')
        seen_tracks = [q.correct_answer for q in self.questions.all()]
        answer = Track.pick_random(exclude=seen_tracks)
        number = self.questions.count() + 1
        question = Question.objects.create(game=self,
                        correct_answer=answer, number=number)
        return question
        
    @staticmethod
    def highscore_queryset():
        return Game.objects.annotate(score=models.Sum('questions__points')) \
                .order_by('-score', '-date_started')
        
    def total_score(self):
        return sum(q.calculate_points() for q in self.questions.all())
        
    def correct_answers(self):
        return sum(1 for q in self.questions.all() if q.answered_correctly())
        
    def has_started(self):
        return self.questions.count() != 0
        
    def current_question(self):
        """Return current question."""
        if not self.has_started():
            raise QuizModelException('game has not started')
        return self.questions.order_by('-number')[0]
        
    def remaining_questions(self):
        return self.quiz_length - self.questions.all().count()
        
    def is_game_finished(self):
        """Check if the game is already finished."""
        
        if not self.questions.count():
            return False
        
        last_question_answered = self.current_question().is_answered()
        all_questions_shown = self.questions.count() == self.quiz_length
        return all_questions_shown and last_question_answered
        
    def __unicode__(self):
        return u'#%d' % (self.id)
