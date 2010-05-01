from django.db import models
from django.conf import settings
from utility import extract_youtube_code
import gdata.youtube
import gdata.youtube.service
import pylast
import random

# Create your models here.

class Song(models.Model):
    """Song model responsible for fetching data from web and storing it."""

    artist = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    youtube_code = models.CharField(max_length=20, null=True, blank=True)
    similar = models.ManyToManyField('self', through='SongSimilarity',
                                     symmetrical=False)
    
    def create_similarity(self, similar, match):
        """Create similarity between songs.
        
        Parameter `match` is a float value which tells how
        similar the two songs are. This method must be used
        to ensure symmetrical relationship.
        
        >>> a = Song.objects.create(artist='A', title='a')
        >>> b = Song.objects.create(artist='B', title='b')
        >>> a.similar.all()
        []
        >>> b.similar.all()
        []
        >>> a.create_similarity(b, 42)
        >>> a.create_similarity(b, 0)
        Traceback (most recent call last):
        ...
        IntegrityError: columns first_id, second_id are not unique
        >>> b in a.similar.all()
        True
        >>> a in b.similar.all()
        True
        >>> b in a.similar.filter(songsimilarity__match=42)
        True
        >>> b in a.similar.filter(songsimilarity__match=43)
        False
        >>> a.delete()
        >>> b.similar.all()
        []
        >>> b.create_similarity(b, 1)
        Traceback (most recent call last):
        ...
        ValueError: song cannot be similar to itself
        """
        if self == similar:
            raise ValueError('song cannot be similar to itself')
        SongSimilarity.objects.create(first=self, second=similar, match=match)
        SongSimilarity.objects.create(first=similar, second=self, match=match)
    
    def remove_similarity(self, similar):
        """Remove similarity between songs.
        
        This method must be used to ensure symmetrical relationship.
        
        >>> a = Song.objects.create(artist='A', title='a')
        >>> b = Song.objects.create(artist='B', title='b')
        >>> a.create_similarity(b, 1)
        >>> b in a.similar.all()
        True
        >>> b.remove_similarity(a)
        >>> b in a.similar.all()
        False
        >>> b.remove_similarity(a)
        Traceback (most recent call last):
        ...
        ValueError: songs are not similar
        """
        if similar not in self.similar.all():
            raise ValueError('songs are not similar')
        self.songsimilarity_set.filter(second=similar)[0].delete()
        similar.songsimilarity_set.filter(second=self)[0].delete()
    
    def fetch_similar(self, limit=25):
        """Fetch a list or similar songs and save them in the database.
        
        Returns the count of newly created similar songs.

        >>> a = Song.objects.create(artist='a', title='a')
        >>> a.fetch_similar(-1)
        Traceback (most recent call last):
        ...
        ValueError: limit must be a positive integer
        """
        if limit < 0:
            raise ValueError('limit must be a positive integer')
        network = pylast.get_lastfm_network(api_key=settings.LASTFM_API_KEY)
        track = network.get_track(self.artist, self.title)
        similar = track.get_similar()
        new_songs = 0
        for track in similar[:limit]:
            name = track.item.artist.name
            title = track.item.title
            obj, flag = Song.objects.get_or_create(artist=name, title=title)
            try:
                self.create_similarity(obj, track.match)
            except IntegrityError, e:
                pass
            else:
                new_songs += 1
        return new_songs

    def update_youtube_code(self):
        """Find video for a song and update youtube code field.
        
        >>> song = Song(artist='Faithless', title='Insomnia')
        >>> song.update_youtube_code()
        >>> song.youtube_code
        'tBrUjvONIrA'
        """
        service = gdata.youtube.service.YouTubeService()
        query = gdata.youtube.service.YouTubeVideoQuery()
        query.vq = '%s %s' % (self.artist, self.title)
        feed = service.YouTubeQuery(query)
        if len(feed.entry) > 0:
            url = feed.entry[0].GetSwfUrl()
            youtube_code = extract_youtube_code(url)
            self.youtube_code = youtube_code
        
    @staticmethod
    def pick_random(exclude=[]):
        """Pick a random song which is not in the exclude list.
        
        >>> Song.pick_random(exclude=Song.objects.all())
        Traceback (most recent call last):
        ...
        ValueError: could not pick any song
        """
        exclude_pks = [song.pk for song in exclude]
        try:
            return random.choice(Song.objects.exclude(pk__in=exclude_pks))
        except IndexError, e:
            raise ValueError('could not pick any song')
        
    def get_possible_answers(self, count=5):
        """Return a list of random possible answers.
        
        >>> song = Song(artist='Radiohead', title='Karma Police')
        >>> song.save()
        
        # Correct answer must be one of the possible answers
        >>> [song in song.get_possible_answers() for i in range(5)]
        [True, True, True, True, True]
        
        >>> song.get_possible_answers(count=0)
        Traceback (most recent call last):
        ...
        ValueError: there must be at least one answer
        
        >>> song.delete()
        """
        if count < 1:
            raise ValueError('there must be at least one answer')
        total = Song.objects.count()
        query = Song.objects.exclude(pk__in=[self.pk])
        answers = random.sample(query, min([total, count]) - 1)
        answers += [self]
        random.shuffle(answers)
        return answers       

    def __unicode__(self):
        """Return a string representation mainly for debugging."""
        return u'%s -- %s (%s)' % (self.artist, self.title, self.youtube_code)
        

class SongSimilarity(models.Model):
    """Intermediate model class to store the similarities of songs."""
    
    first = models.ForeignKey(Song)
    second = models.ForeignKey(Song, related_name='similar_songs')
    match = models.FloatField(null=True)
    
    class Meta:
        unique_together = (('first', 'second'),)
    
    def __unicode__(self):
        """Return a string representation mainly for debugging."""
        return u'%s <-> %s (%f)' % (self.first, self.second, self.match)
        

class Question(models.Model):
    """Model class for quiz question."""
    
    good_choice = models.ForeignKey(Song)
    other_choices = models.ManyToManyField(Song, related_name='in_answer')
    
    times_answered = models.IntegerField()
    times_answered_correctly = models.IntegerField()
    
    def make_guess(self, song):
        pass
    
    def __unicode__(self):
        """Return a string representation mainly for debugging."""
        return u'%s' % (self.correct)
