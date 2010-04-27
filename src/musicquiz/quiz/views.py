from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from models import Song
from forms import WelcomeForm
from forms import AnswerForm

def index(request):
    """Show index page with the welcome form."""
    if request.method == 'POST':
        form = WelcomeForm(request.POST)
        if form.is_valid():
            request.session['username'] = form.cleaned_data['name']
            return HttpResponseRedirect('question/')
    else:
        form = WelcomeForm()
    return render_to_response('quiz/index.html', {
        'form' : form,
    })
    
def show_question(request):
    """Show a randomly chosen question to the visitor."""    
    if 'username' not in request.session.keys():
        return HttpResponseRedirect('/quiz/')
    prev_result = None
    if request.method == 'POST' and 'current_song' in request.session.keys():
        current = request.session['current_song']
        prev_result = {
            'correct' : request.POST['answer'] == str(current.pk)
        }
    song = Song.pick_random()
    request.session['current_song'] = song
    possible_answers = song.get_possible_answers()
    choices = [(item.pk, item) for item in possible_answers]
    answer_form = AnswerForm(choices)
    return render_to_response('quiz/question.html', {
        'answer_form' : answer_form,
        'song' : song,
        'prev_result' : prev_result,
        'name' : request.session['username'],
    })
