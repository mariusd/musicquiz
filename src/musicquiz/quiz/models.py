from django.db import models
from django.db import IntegrityError
from django.conf import settings
from utility import extract_youtube_code
from tagging.models import TaggedItem
import gdata.youtube
import gdata.youtube.service
import pylast
import random
import urllib
import tagging

EPSILON = 1e-9

network = pylast.get_lastfm_network(api_key=settings.LASTFM_API_KEY)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass
    
class QuizModelError(Error):
    """Exception class.
    
    New exception classes may be declared in the future for some special
    situations in this module, but for now all errors use this class.
    """
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

    def __unicode__(self):
        return repr(self.value)
 
 
# Create your models here.

class Artist(models.Model):
    """Artist model class."""
    
    name = models.CharField(max_length=128)
    
    def fetch_similar(self):
        """Fetch similar artists from last.fm database."""
        
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
    def pick_random(exclude=[], tag=None):
        """Pick a random track which is not in the exclude list.
        
        Returned track is guaranteed to have youtube code and duration.
        """
        
        exclude_pks = [track.pk for track in exclude]
        try:
            if not tag:
                track_objects = Track.objects
            else:
                tagged_obj = TaggedItem.objects
                track_objects = tagged_obj.get_by_model(Track, tag)
            track = random.choice(track_objects.exclude(pk__in=exclude_pks))
        except IndexError, e:
            raise ValueError('could not pick any track')
        else:
            if not track.has_youtube_info():
                track.update_youtube_info()
            if track.has_youtube_info():
                return track
            else:
                return Track.pick_random(exclude=exclude + [track], tag=tag)
    
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
                
    @staticmethod
    def _save_lastfm_result(pylast_track_result):
        """Save the result from pylast query to database.
        
        Returns the list of tuples (track, flag), where flag tells
        whether the track was created or was it already in the database.
        """
        result = []
        for pylast_track in pylast_track_result:
            artist_name = pylast_track.item.artist.name
            title = pylast_track.item.title
            artist, _ = Artist.objects.get_or_create(name=artist_name)      
            res = Track.objects.get_or_create(artist=artist, title=title)
            result.append(res)
        return result
            
    def fetch_similar(self, limit=None):
        """Fetch a list of similar tracks and save them in the database.
        
        Returns the count of newly added tracks.
        """
        
        if limit is not None and limit < 0:
            raise ValueError('limit must be a positive integer')
        global network
        lastfm_track = network.get_track(unicode(self.artist), self.title)
        similar = lastfm_track.get_similar()
        
        if limit is not None:
            similar = similar[:limit]
            
        new_tracks = Track._save_lastfm_result(similar)
        return sum(1 for (track, flag) in new_tracks if flag)
        
    @staticmethod
    def fetch_top_tracks(tag):
        """Get most popular tracks tagged with a specified tag.
        
        Returns the count of newly added tracks.
        """
        
        global network
        lastfm_tag = network.get_tag('%s' % tag)
        
        try:
            top_tracks = lastfm_tag.get_top_tracks()
        except pylast.WSError, e:
            top_tracks = []
            
        new_tracks = Track._save_lastfm_result(top_tracks)
        for track, flag in new_tracks:
            tagging.models.Tag.objects.add_tag(track, '"%s"' % tag)
        return sum(1 for (track, flag) in new_tracks if flag)
    
    def __unicode__(self):
        return u'%s \u2013 %s' % (self.artist, self.title)
        
tagging.register(Track)

    
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
        """Check if the user has reacted in some way to the question."""
        
        return self.state != 'NOANSWER'
        
    def answered_correctly(self):
        """Check if the question was answered correctly."""
    
        return self.correct_answer == self.given_answer
        
    def make_guess(self, guess):
        """Try to guess the answer.
        
        Dictionary `guess` must contain 'answer' and 'remaining_time' keys.
        """
    
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
        """Recalculate the question point field and return its value."""
    
        if self.answered_correctly():
            self.points = self.remaining_time
        elif self.state == 'ANSWERED' and not self.answered_correctly():
            self.points = -10
        else:
            self.points = 0
        self.save()
        return self.points
        
    def skip_question(self):
        """Skip question."""
    
        self.given_answer = None
        self.remaining_time = None
        self.state = 'SKIPPED'
        self.calculate_points()
        self.save()
        
    def is_timeout(self):
        """Check if the question was answered in time."""
        
        return self.state == 'TIMEOUT'
        
    def create_choices(self, count=8):
        """Return a list of randomly selected possible answers.
        
        Correct answer is always one of the possible choices, but
        other tracks in the list are very likely to be different
        each time this method gets called.
        """
        
        if count < 1:
            raise ValueError('there must be at least one answer')
        if not self.game.tags:
            tracks_with_tag = 0
        else:
            tracks_with_tag = (count + 1) / 2
            
        choices = [self.correct_answer]
        
        if tracks_with_tag:
            tagged_obj = TaggedItem.objects
            tag = self.game.tags[0]
            track_objects = TaggedItem.objects.get_by_model(Track, tag)
            query = track_objects.exclude(pk__in=[self.correct_answer.pk])
            choices += random.sample(query, tracks_with_tag)
        
        if count - tracks_with_tag - 1 > 0:
            exclude_list = [t.pk for t in choices]
            query = Track.objects.exclude(pk__in=exclude_list)
            choices += random.sample(query, count - tracks_with_tag - 1)
            
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
            
        if self.questions.count() == self.quiz_length:
            raise QuizModelError('there are no more questions left')
        
        seen_tracks = [q.correct_answer for q in self.questions.all()]
        if not self.tags:
            answer = Track.pick_random(exclude=seen_tracks)
        else:
            tag = self.tags[0]
            answer = Track.pick_random(exclude=seen_tracks, tag=tag)
        number = self.questions.count() + 1
        question = Question.objects.create(game=self,
                        correct_answer=answer, number=number)
        return question
        
    @staticmethod
    def highscore_queryset():
        """Return the QuerySet for the list of top scorers.
        
        If two players have equal scores, the newer one is rated better.
        This is needed to eliminate the possibility that a player makes
        a perfect score and then stays in the first position forever. 
        """

        return Game.objects.annotate(score=models.Sum('questions__points')) \
                .order_by('-score', '-date_started')
        
    def total_score(self):
        """Return total score."""
    
        return sum(q.calculate_points() for q in self.questions.all())
        
    def correct_answers(self):
        """Return the number of correctly in time answered questions."""
    
        return sum(1 for q in self.questions.all()
                        if q.answered_correctly() and not q.is_timeout())
        
    def has_started(self):
        """Check if the game has started.
        
        The game starts when user requests the first question.
        """
        
        return self.questions.count() != 0
        
    def current_question(self):
        """Return current question."""
        
        if not self.has_started():
            raise QuizModelError('game has not started')
        if self.is_game_finished():
            raise QuizModelError('game is already over')
            
        return self.questions.order_by('-number')[0]
        
    def remaining_questions(self):
        """Return the number of remaining questions."""
    
        return self.quiz_length - self.questions.all().count()
        
    def is_game_finished(self):
        """Check if the game has already finished."""
        
        if self.questions.count() != self.quiz_length:
            return False
        
        last_question = self.questions.get(number=self.quiz_length)
        return last_question.is_answered()
        
    def __unicode__(self):
        return u'#%d' % (self.id)

tagging.register(Game)