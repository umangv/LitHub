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
from django.utils.http import urlencode
from django.conf import settings
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
