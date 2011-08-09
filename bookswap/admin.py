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

from bookswap.models import Book, Copy
from django.contrib import admin

class CopyInline(admin.StackedInline):
    model = Copy
    extra = 1

class BookAdmin(admin.ModelAdmin):
    fieldsets = [
            (None, {'fields':['isbn', 'title', 'author', 'publisher',
                'copyrightYear']})]
    inlines = [CopyInline]

admin.site.register(Book, BookAdmin)
admin.site.register(Copy)
