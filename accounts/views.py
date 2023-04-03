from django.shortcuts import render
from .forms import RegestrationForm
from .models import Account
from django.contrib import messages,auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#verrifications email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

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

            #User activation
            current_site=get_current_site(request)
            mail_subject="Please activate your account"
            message=render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #this is to encode the uid by the encoder so that no other person can see the uid
                'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email]) #this is to send the email, what to send, where to send
            send_email.send()
            messages.success(request,'Regestration success. Please use the activation link to continue.')


            return redirect('/accounts/login/?command=verification&email='+email) #this will show if the user came from registration form or not
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
            return redirect('dashboard')
        else:
            messages.error(request,"Invalid login details")
            return redirect ('login')

    return render(request,'accounts/login.html')

@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request,"You're logged out.")
    return redirect('login')



def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulation! Your account is activated')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link.')
        return redirect('register')
    

@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgotPassword(request):
    if request.method=='POST':
        email=request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email) #if the email is being enter is exact similar to email in our database

            #resetpassword email
            current_site=get_current_site(request)
            mail_subject="Reset Your Password"
            message=render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #this is to encode the uid by the encoder so that no other person can see the uid
                'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email]) #this is to send the email, what to send, where to send
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')


        else:
            messages.error(request,'Account does not exist.')    
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')
    
def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        request.session["uid"]=uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('login')


def resetPassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password) #here set password is in build function in django which let us use save the updated password in database automatically in hased format
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')

        else:
            messages.error(request,'Password do not match')
            return redirect('resetPassword')

    return render(request,'accounts/resetPassword.html')