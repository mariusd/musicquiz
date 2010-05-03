from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from models import Song
from forms import WelcomeForm
from forms import AnswerForm

def index(request):
    """Show index page with the welcome form.
    
    >>> import django.test
    >>> from django.core.urlresolvers import reverse
    >>> django.test.utils.setup_test_environment()
    >>> c = django.test.Client()
    >>> index = reverse('musicquiz.quiz.views.index')
    >>> response = c.get(index)
    >>> response.status_code
    200
    >>> response.context['form'] #doctest: +ELLIPSIS
    <musicquiz.quiz.forms.WelcomeForm object at ...>
    
    # Submitting a correct name causes a redirect
    >>> response = c.post(index, { 'name' : 'Mr. User Name' })
    >>> response.status_code
    302
    """
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
    """Show a randomly chosen question to the visitor.
    
    >>> import django.test
    >>> from django.core.urlresolvers import reverse
    >>> django.test.utils.setup_test_environment()
    >>> c = django.test.Client()
    >>> question = reverse('musicquiz.quiz.views.show_question')
    
    # Anonymous visitors are redirected back to index page
    >>> response = c.get(question)
    >>> response.status_code
    302
    
    >>> index = reverse('musicquiz.quiz.views.index')
    
    # Tests need data
    #>>> response = c.post(index, { 'name' : 'Mr. Foo Bar' }, follow=True)
    """    
    if 'username' not in request.session.keys():
        return HttpResponseRedirect('/quiz/')
        
    prev_result = None
    if request.method == 'POST' and 'current_song' in request.session.keys():
        current = request.session['current_song']
        if request.POST['timeout_flag'] == 'true':
            prev_result = {
                'class' : 'error',
                'message' : 'Time is up.',
            }
        elif request.POST['answer'] == str(current.pk):
            prev_result = {
                'class' : 'success',
                'message' : 'Congratulations! You have answered correctly!',
            }
        else:
            prev_result = {
                'class' : 'error',
                'message' : 'Your answer was incorrect.',
            }
            
    song = Song.pick_random()
    request.session['current_song'] = song
    possible_answers = song.get_possible_answers(count=8)
    choices = [(item.pk, item.get_label()) for item in possible_answers]
    return render_to_response('quiz/question.html', {
        'choices' : choices,
        'song' : song,
        'prev_result' : prev_result,
        'name' : request.session['username'],
    })
