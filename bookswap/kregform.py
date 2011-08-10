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
from registration.backends.default import DefaultBackend
from django import forms

class KzooRegistrationForm(RegistrationFormUniqueEmail):
    """Registration form with modifications for Kzoo LitHb
    
    This adds the first and last name fields and verifies that the user has
    a valid @kzoo.edu email address."""
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    def clean_email(self):
        """Ensures a valid K student email id is used. """
        email_parts = self.cleaned_data['email'].split('@')
        if email_parts[1].lower () != "kzoo.edu":
            raise forms.ValidationError("Only @kzoo.edu addresses " +\
                    "are allowed!")
        email_u = email_parts[0].lower()
        if email_u[0] == 'k' and email_u[1:3].isdigit():
            raise forms.ValidationError("To avoid duplicate accounts, "+\
                    "abbreviated email ids (e.g. k99zz01@kzoo.edu) are " +\
                    "not allowed on Kzoo LitHub.")
        return super(KzooRegistrationForm, self).clean_email()

class KzooRegistrationBackend(DefaultBackend):
    """Registration backend that adds first and last name to the user"""
    def register(self, request, **kwargs):
        user = super(KzooRegistrationBackend, self).register(request, **kwargs)
        user.first_name = kwargs['first_name']
        user.first_name = kwargs['last_name']
        user.save()
        return user
