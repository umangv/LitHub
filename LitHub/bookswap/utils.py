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

import urllib2
import isbn
import datetime
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage, Page
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
import json

def get_book_details(isbn_no):
    try:
        isbn_no = isbn.clean_isbn(isbn_no)
        lookup_url = "https://www.googleapis.com/books/v1/volumes?"
        opts = {'q':'isbn:%s'%isbn_no}
        if hasattr(settings, "GOOGLE_API_KEY"):
            opts['key'] = settings.GOOGLE_API_KEY
        google_resp = urllib2.urlopen(lookup_url + urlencode(opts))
        results = json.loads(google_resp.read())
        google_resp.close()
        if int(results['totalItems']) > 0:
            info = {}
            # Choose the first item, regardless of anything else
            item = results['items'][0]
            vol = item['volumeInfo']
            info['title'] = vol.get('title')
            authors = vol.get('authors')
            if len(authors) > 1:
                info['author'] = "%s and %s"%(", ".join(authors[:-1]),
                        authors[-1])
            else:
                info['author'] = authors[0]
            info['copyrightYear'] = vol.get('publishedDate', '').split("-")[0]
            info['publisher'] = vol.get('publisher', '')
            info['thumbnail_url'] = (vol.get('imageLinks') or
                    {'na':'na'}).get('thumbnail', '')
            return info
    except Exception:
        return None

def opengraph_list_book(request, copy):
    from fbconnect import utils as fbutils
    fb_at = request.session.get('fb_at', '')
    if fb_at:
        fb = fbutils.FBConnect(access_token=fb_at)
        try:
            params = {'expires_in': 60*60*24*3}
            fb.publish_og('list', 'book', settings.FB_REDIRECT_URL +\
                    reverse('bookswap.views.book_details',
                        args=[copy.book.id]), params=params)
            return True
        except ValueError:
            return False
        # an access_token can sometimes expire and we cannot do anything to
        # prevent it from doing so if we don't have offline access
    else:
        return False

class PaginatorN(Paginator):
    GET_PAGE_VAR = 'p'
    def __init__(self, object_list, request, per_page=12, *args, **kwargs):
        self.request = request
        Paginator.__init__(self, object_list, per_page, \
                *args, **kwargs)

    def page(self, number):
        class PageN(Page):
            def __init__(self, page):
                self.__dict__ = page.__dict__
        try:
            return Paginator.page(self, number)
        except (EmptyPage, InvalidPage):
            return Paginator.page(self, self.num_pages)

    def page_auto(self):
        try:
            page = int(self.request.GET.get(self.GET_PAGE_VAR, '1'))
        except ValueError:
            page = 1
        return self.page(page)

    def other_get_vars(self):
        opts = self.request.GET.copy()
        try:
            opts.pop(self.GET_PAGE_VAR)
        except KeyError:
            pass
        if opts:
            return "?%s&%s="%(opts.urlencode(), self.GET_PAGE_VAR)
        else:
            return "?%s="%self.GET_PAGE_VAR
