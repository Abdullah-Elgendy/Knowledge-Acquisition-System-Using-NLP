from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def renderHome(request):
    
    if request.user.is_authenticated:
        redirect('userhome')
    
      
    return render(request , 'Homepage/index.html' )

@login_required
def renderUserhome(request):
    
    return render(request , 'Homepage/userhome.html' )
