from django import forms
from .models import Account,UserProfile

class RegestrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control',
    }))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Password',
        'class':'form-control',
    }))
    
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email','password']

    def __init__(self,*args,**kwarg):
        super(RegestrationForm,self).__init__(*args,**kwarg)
        self.fields['first_name'].widget.attrs['placeholder']='Enter Firstname'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Lastname'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter your email'
        self.fields['password'].widget.attrs['placeholder']='Enter password'
        self.fields['last_name'].widget.attrs['placeholder']='Confirm password '


        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

    def clean(self): #this function will check if the password and confirm password are same or not.
        cleaned_data=super(RegestrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password!=confirm_password:
            raise forms.ValidationError(
                "Password doesnot match!"
            )
        

class UserForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=('first_name','last_name','last_name')


    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class UserProfileForm(forms.ModelForm):
    class Meta:
        model=UserProfile
        fields=('address_line_1','address_line_2','city','state')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'