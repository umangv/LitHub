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

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView
from django import forms

class KzooRegistrationForm(RegistrationFormUniqueEmail):
    """Registration form with modifications for Kzoo LitHb
    
    This adds the first and last name fields and verifies that the user has
    a valid kzoo.edu email address."""
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    def clean_email(self):
        """Ensures a valid K student email id is used. """
        email_parts = self.cleaned_data['email'].split('@')
        if email_parts[1].lower () != "kzoo.edu":
            raise forms.ValidationError("Only kzoo.edu addresses " +\
                    "are allowed!")
        return super(KzooRegistrationForm, self).clean_email()

class KRegistrationView(RegistrationView):
    form_class = KzooRegistrationForm

    """Registration backend that adds first and last name to the user"""
    def register(self, request, **cleaned_data):
        user = super(KRegistrationView, self).register(request,
                **cleaned_data)
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.save()
        return user
