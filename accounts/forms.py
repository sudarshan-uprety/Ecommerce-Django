from django import forms
from .models import Account


class RegestrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter Password",
                "class": "form-control",
            }
        ),
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control",
            }
        ),
        min_length=6
    )

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def __init__(self, *args, **kwarg):
        super(RegestrationForm, self).__init__(*args, **kwarg)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter Firstname"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Lastname"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Enter Phone Number"
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email"
        self.fields["password"].widget.attrs["placeholder"] = "Enter password"

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean(
        self,
    ):  # this function will check if the password and confirm password are same or not.
        cleaned_data = super(RegestrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password doesnot match!")
