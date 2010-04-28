from django.db import models
import gdata.youtube
import gdata.youtube.service
import random
import urlparse

def extract_youtube_code(url):
    """Extract youtube video code (e.g. EjAoBKagWQA) from url.
    
    >>> eyc = extract_youtube_code
    >>> eyc('http://www.youtube.com/watch?v=qndUS3SIf1Q&feature=related')
    'qndUS3SIf1Q'
    >>> eyc('http://youtube.com/v/3Ii8m1jgn_M?f=videos&app=youtube_gdata')
    '3Ii8m1jgn_M'
    >>> eyc('http://www.youtube.com/watch?WRONG=qndUS3SIf1Q')
    Traceback (most recent call last):
    ...
    ValueError: cannot extract code (wrong url?)
    """
    result = urlparse.urlparse(url, scheme='http')
    if result.path == '/watch':
        parse_query = urlparse.parse_qs(result.query)
        if 'v' in parse_query.keys():
            return parse_query['v'][0]
    elif result.path[:3] == '/v/':
        return result.path[3:]
    raise ValueError('cannot extract code (wrong url?)')

# Create your models here.

class Song(models.Model):
    artist = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    youtube_code = models.CharField(max_length=20, null=True, blank=True)
    
    def get_similar(self):
        """Get a list of similar songs."""
        pass
        
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
        return '%s -- %s (%s)' % (self.artist, self.title, self.youtube_code)
