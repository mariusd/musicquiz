from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from forms import WelcomeForm

def index(request):
    if request.method == 'POST':
        form = WelcomeForm(request.POST)
        if form.is_valid():
            request.session['username'] = form.cleaned_data['name']
            return HttpResponseRedirect('session/')
    else:
        form = WelcomeForm()
    return render_to_response('quiz/index.html', { 'form' : form, })
    
def show_session(request):
    return render_to_response('quiz/test.html', { 'data' : request.session, })
