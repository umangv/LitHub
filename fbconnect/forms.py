from django import forms
from django.contrib.auth.models import User

class FBRegisterForm(forms.Form):
    username = forms.CharField(max_length=30)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count():
            raise forms.ValidationError("This username has already been "+\
                    "taken. Please try again")
        if username.lower() != username:
            raise forms.ValidationError("Username has to be lower case!")
        return self.cleaned_data['username']
