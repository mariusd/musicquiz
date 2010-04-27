from django.db import models
import random

# Create your models here.

class Song(models.Model):
    artist = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    youtube_code = models.CharField(max_length=20, null=True, blank=True)
    
    def get_similar(self):
        """Get a list of similar songs."""
        pass
        
    def update_youtube_code(self):
        """Find video for a song and update youtube code field."""
        pass
        
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
