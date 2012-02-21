#    Copyright 2010, 2011 Kalamazoo College Computer Science Club
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
from models import COPY_CONDITIONS, Book, Copy, Feedback
from datetime import datetime
import isbn 

class ContactForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ('date')

class SellExistingBookForm(forms.ModelForm):
    class Meta:
        model = Copy
        fields = ('price', 'condition', 'comments')

class SellNewBookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('isbn','thumbnail_url', 'subscribers')

class SearchTitleAuthorForm(forms.Form):
    title = forms.CharField(max_length=200)
    author = forms.CharField(max_length=200)

class SearchISBNForm(forms.Form):
    isbn = forms.CharField(max_length=15)

    def clean_isbn(self):
        try:
            return isbn.clean_isbn(self.cleaned_data['isbn'])
        except ValueError:
            raise forms.ValidationError('Invalid ISBN')

class EditCopyForm(forms.ModelForm):
    class Meta:
        model = Copy
        exclude = ('owner', 'book','soldTime', 'pubDate',)

class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
