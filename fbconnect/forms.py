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
        if username.lower() != username:
            raise forms.ValidationError("Username has to be lower case!")
        return self.cleaned_data['username']
