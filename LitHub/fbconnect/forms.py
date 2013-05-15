#    Copyright 2011 Kalamazoo College Computer Science Club
#    <kzoo-cs-board@googlegroups.com>

#    This file is part of LitHub.
#
#    LitHub is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    LitHub is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with LitHub.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.contrib.auth.models import User

class FBRegisterForm(forms.Form):
    username = forms.CharField(max_length=30)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count():
            raise forms.ValidationError("This username has already been "+\
                    "taken. Please try again")
        return self.cleaned_data['username']

class FBRegisterVerifyForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count():
            raise forms.ValidationError("This username has already been "
                    "taken. Please try again")
        return self.cleaned_data['username']

    def clean_email(self):
        """Ensures a valid K student email id is used. """
        email_parts = self.cleaned_data['email'].split('@')
        if email_parts[1].lower () != "kzoo.edu":
            raise forms.ValidationError("Only kzoo.edu addresses are "
                    "allowed!")
        return self.cleaned_data['email']
