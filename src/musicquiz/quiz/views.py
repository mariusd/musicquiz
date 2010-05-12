from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from tagging.models import Tag
from tagging.models import TaggedItem

from models import Game
from models import Track
from utility import create_fragment

def index(request):
    """Show the index page."""
    
    if request.method == 'POST':
        question_url = reverse('musicquiz.quiz.views.question')
        quiz_tag = request.POST['quiz_tag'].strip()
        if len(quiz_tag) > 0:
            return new_game(request, tag=quiz_tag)
        else:
            return new_game(request)
    
    if 'game' in request.session.keys():
        current_game = request.session['game']
        if Game.objects.filter(pk=current_game.pk).count() == 0:
            current_game = 0
            del request.session['game']
    else:
        current_game = None
                
    return render_to_response('quiz/index.html', {
        'current_game' : current_game,
    })
    
    
def new_game(request, tag=None):
    """Start new game."""
    
    new_game = Game.objects.create(quiz_length=10)
    if tag:
        Track.fetch_top_tracks(tag)
        tag_object, _ = Tag.objects.get_or_create(name='%s' % tag)
        tagged = TaggedItem.objects.get_by_model(Track, tag_object)
        tracks_with_tag = tagged.count()
        if tracks_with_tag == 0:
            tag_object.delete()
        if tracks_with_tag < 20:
            err = ''.join(['There is not enough data to create a quiz. ',
                                'Please choose a more popular tag.'])
            new_game.delete()
            return render_to_response('quiz/index.html', {
                'error_msg' : err,
                'current_game' : None,
            })
        else:
            new_game.tags = '"%s"' % tag

    request.session['game'] = new_game    
    question_url = reverse('musicquiz.quiz.views.question')
    return HttpResponseRedirect(question_url)
    
   
def stats(request):
    """Show stats of the currently going (or finished) game."""
    
    if 'game' not in request.session.keys():
        return HttpResponseRedirect(reverse('musicquiz.quiz.views.index'))
        
    current_game = request.session['game']
    score = current_game.total_score()
    
    highscore_iter = Game.highscore_queryset().iterator()
    fragment, pos = create_fragment(highscore_iter, current_game, 5)
    indexed_games = [(pos + i + 1, game) for i, game in enumerate(fragment)]
    
    return render_to_response('quiz/stats.html', {
        'total_score' : score,
        'this_game' : current_game,
        'other_scores' : indexed_games,
        'questions' : current_game.questions.all(),
    })
    
    
def highscores(request, page_number=1):
    """Show summary of all games (highscore table)."""
    
    highscore_iter = Game.highscore_queryset().iterator()
    scores = [(pos + 1, game) for pos, game in enumerate(highscore_iter)]
    paginator = Paginator(scores, 10)
    try:
        scores = paginator.page(page_number)
    except InvalidPage:
        scores = paginator.page(1)
    
    return render_to_response('quiz/highscores.html', {
        'scores' : scores,
    })
    
    
def question(request):
    """Handle player's submitted answer, then select the next question
    and show it to the player. If there are no more questions, visitor
    is redirected to the stats page.
    """
    
    if 'game' not in request.session.keys():
        return HttpResponseRedirect(reverse('musicquiz.quiz.views.index'))
        
    game = request.session['game']
    
    if request.method == 'POST':
        current_question = game.current_question()
        guess_data = { }
        remaining_time = float(request.POST['remaining_time'])
        guess_data['remaining_time'] = remaining_time
        if 'answer' in request.POST.keys():
            guess_data['answer'] = int(request.POST['answer'])
        current_question.make_guess(guess_data)
        
        if current_question.is_timeout():
            prev_result = {
                'class' : 'error',
                'message' : 'Time is up.',
            }
        elif current_question.answered_correctly():
            prev_result = {
                'class' : 'success',
                'message' : 'Congratulations! You have answered correctly!',
            }
        else:
            prev_result = {
                'class' : 'error',
                'message' : 'Wrong.',
            }
        prev_result['correct'] = current_question.correct_answer
    elif game.has_started() and not game.is_game_finished():
        current_question = game.current_question()
        prev_result = {
            'class' : 'notice',
            'message' : 'Question was skipped.',
        }
        prev_result['correct'] = current_question.correct_answer
        current_question.skip_question()
    else:
        prev_result = None
        
    if game.is_game_finished():
        game_history_url = reverse('musicquiz.quiz.views.stats')
        return HttpResponseRedirect(game_history_url)
    
    next_question = game.next_question()
    possible_answers = next_question.create_choices()
    choices = [(item.pk, unicode(item)) for item in possible_answers]
    return render_to_response('quiz/question.html', {
        'choices' : choices,
        'length' : game.quiz_length,
        'question' : next_question,
        'prev_result' : prev_result,
    })
