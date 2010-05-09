from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage

from models import Game
from forms import WelcomeForm
from forms import AnswerForm

import collections

def index(request):
    """Show index page with the welcome form."""
    
    if request.method == 'POST':
        question_url = reverse('musicquiz.quiz.views.question')
        return new_game(request)
    
    if 'game' in request.session.keys():
        current_game = request.session['game']
    else:
        current_game = None
                
    return render_to_response('quiz/index.html', {
        'current_game' : current_game,
    })
    
    
def new_game(request):
    """Start new game."""
    
    request.session['game'] = Game.objects.create(quiz_length=10)
    question_url = reverse('musicquiz.quiz.views.question')
    return HttpResponseRedirect(question_url)
    
   
def stats(request):
    """Show stats of the currently going (or finished) game."""
    
    if 'game' not in request.session.keys():
        return HttpResponseRedirect(reverse('musicquiz.quiz.views.index'))
        
    current_game = request.session['game']
    score = current_game.total_score()
    
    highscore_iter = Game.highscore_queryset().iterator()
    
    def create_fragment(iter, obj, size):
        fragment = collections.deque()
        last_removed = collections.deque()
        current_added = False
        for index, element in enumerate(iter):
            fragment.append((index + 1, element))
            if element == obj:
                current_added = True
            if not current_added and len(fragment) == (size + 1) / 2:
                last_removed.append(fragment.popleft())
                if len(last_removed) > size:
                    last_removed.popleft()

            if len(fragment) == size:
                break
        else:
            for removed in reversed(last_removed):
                fragment.appendleft(removed)
                if len(fragment) == size:
                    break
        return fragment
    
    highscore_fragment = create_fragment(highscore_iter, current_game, 5)
        
    return render_to_response('quiz/stats.html', {
        'total_score' : score,
        'this_game' : current_game,
        'other_scores' : highscore_fragment,
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
    """Select and show next question to the player."""
    
    if 'game' not in request.session.keys():
        return HttpResponseRedirect(reverse('musicquiz.quiz.views.index'))
        
    game = request.session['game']
    
    prev_result = None
    if request.method == 'POST':
        current_question = game.current_question()
        guess_data = { }
        remaining_time = float(request.POST['remaining_time'])
        guess_data['remaining_time'] = remaining_time
        if 'answer' in request.POST.keys():
            guess_data['answer'] = int(request.POST['answer'])
        current_question.make_guess(guess_data)
        
        if current_question.answered_correctly():
            prev_result = {
                'class' : 'success',
                'message' : 'Congratulations! You have answered correctly!',
            }
        elif current_question.is_timeout():
            prev_result = {
                'class' : 'error',
                'message' : 'Time is up.',
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
    
    if game.is_game_finished():
        game_history_url = reverse('musicquiz.quiz.views.stats')
        return HttpResponseRedirect(game_history_url)
    
    next_question = game.next_question()
    possible_answers = next_question.get_choices()
    choices = [(item.pk, unicode(item)) for item in possible_answers]
    return render_to_response('quiz/question.html', {
        'choices' : choices,
        'length' : game.quiz_length,
        'question' : next_question,
        'prev_result' : prev_result,
    })
