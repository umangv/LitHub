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

from bookswap.models import Book, Copy, Feedback
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User 
from django.contrib import messages

class CopyInline(admin.StackedInline):
    model = Copy
    extra = 1

class BookAdmin(admin.ModelAdmin):
    fieldsets = [
            (None, {'fields':['isbn', 'title', 'author', 'publisher',
                'copyrightYear', 'thumbnail_url', 'subscribers']})]
    inlines = [CopyInline]
    filter_horizontal = ['subscribers']
    actions = ['update_thumbnail']

    def update_thumbnail(self, request, queryset):
        from utils import get_book_details
        for b in queryset:
            info = get_book_details(b.isbn)
            if info:
                b.thumbnail_url = info['thumbnail_url']
            b.save()
        self.message_user(request, "%s rows updated"%queryset.count())

class CustomUserAdmin(UserAdmin):
    actions = ['send_email']
    list_per_page = 50 # Server can crash if too many emails are sent

    def send_email(self, request, queryset):
        """Sends email to selected users using templates on server.

        The templates are as follows:
        templates/bookswap/mass_email_sub.html - one line subject
        templates/bookswap/mass_email_body.html - HTML body
        templates/bookswap/mass_email_body.txt - text body"""
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        from django.core import mail
        emails = []
        for user in queryset:
            sub = render_to_string('bookswap/mass_email_sub.html', {'user':
                user}).split("\n")[0]
            e = EmailMultiAlternatives()
            e.subject = sub
            e.to = [user.email,]
            e.body = render_to_string('bookswap/mass_email_body.txt', 
                    {'user':user})
            e.attach_alternative(render_to_string(
                'bookswap/mass_email_body.html', {'user':user}), "text/html")
            emails.append(e)
        connection = mail.get_connection()
        connection.send_messages(emails)
        messages.success(request, "Emails sent!")

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Copy)
admin.site.register(Feedback)
