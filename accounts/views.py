from django.shortcuts import render
from .forms import RegestrationForm
from .models import Account
from django.contrib import messages,auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

def register(request):
    if request.method=='POST':
        form=RegestrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name'] #when we use django form we need to use cleaned_data to extract form the frontend
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            phone_number=form.cleaned_data['phone_number']
            password=form.cleaned_data['password']
            username=email.split("@")[0]

            user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)  #this will call the create_user function which is under accounts/mode.py/MyAccountManager class
            user.phone_number=phone_number
            user.save()
            messages.success(request,'Regestration successful')
            return redirect('register')
    else:
        form=RegestrationForm()

    
    context={
        'form':form,
    }
    return render(request,'accounts/register.html',context)



def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']


        user=auth.authenticate(email=email,password=password)


        if user is not None:
            auth.login(request,user)
            #messages.success(request,"you're now logged in")
            return redirect('home')
        else:
            messages.error(request,"Invalid login details")
            return redirect ('login')

    return render(request,'accounts/login.html')

@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request,"You're logged out.")
    return redirect('login')
