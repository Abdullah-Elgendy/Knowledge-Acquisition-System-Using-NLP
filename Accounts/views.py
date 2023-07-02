from django.shortcuts import render ,redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from django.contrib import messages

def renderRegisterPage(request):
    if request.user.is_authenticated:
       return redirect('userhome')
    
    else:
        form = CreateUserForm()
        
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            
            if form.is_valid():
                form.save()
                namevalue = form.cleaned_data.get('username')
                messages.success(request, 'User ' + namevalue + ' was created successfully')
                return redirect('login')
       
        context = {'form':form}
        return render(request, 'Accounts/signup.html', context)


def renderLoginPage(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
    
            if user is not None:
                login(request,user)
                return redirect('userhome')
            else:
                messages.info(request, 'Username or Password is incorrect')
                
       
        return render(request, 'Accounts/login.html')


def logoutUser(request): 
    logout(request)
    return redirect('Home')
    
    
def renderForgotPassword(request):
    
    return render(request , 'Accounts/forgotpassword.html' )




