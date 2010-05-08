from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import Game
from forms import WelcomeForm
from forms import AnswerForm

def index(request):
    """Show index page with the welcome form."""
    
    if request.method == 'POST':
        question_url = reverse('musicquiz.quiz.views.question')
        return new_game(request)
            
    return render_to_response('quiz/index.html')
    
    
def new_game(request):
    """Start new game."""
    request.session['game'] = Game.objects.create(quiz_length=10)
    question_url = reverse('musicquiz.quiz.views.question')
    return HttpResponseRedirect(question_url)
    
    
def game_history(request):
    """Show stats of the currently going (or finished) game."""
    pass
    
    
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
    elif game.has_started():
        current_question = game.current_question()
        prev_result = {
            'class' : 'notice',
            'message' : 'Question was skipped.',
        }
        prev_result['correct'] = current_question.correct_answer
        current_question.skip_question()
    
    if game.is_game_finished():
        game_history_url = reverse('musicquiz.quiz.views.game_history')
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
