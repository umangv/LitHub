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

from django.utils.http import urlquote, urlencode
from django.conf import settings
import urllib2
from urlparse import parse_qs
import json

def get_access_token(code):
    LOOKUP_URL = "https://graph.facebook.com/oauth/access_token?"
    opts = {'client_id':settings.FB_APP_ID,
            'redirect_uri':settings.FB_REDIRECT_URL,
            'client_secret':settings.FB_APP_SECRET,
            'code':code}
    try:
        fb_resp = urllib2.urlopen(LOOKUP_URL + urlencode(opts))
        result = fb_resp.read()
        fb_resp.close()
    except urllib2.HTTPError:
        raise ValueError("The code was invalid or there was a problem" +\
                "connecting to facebook")
    resp = parse_qs(result)
    if not resp.has_key('access_token'):
        raise ValueError("No access token returned")
    return resp['access_token'][0]

def get_basic_info(access_token):
    LOOKUP_URL = "https://graph.facebook.com/me?"
    opts = {'access_token':access_token,}
    try:
        fb_resp = urllib2.urlopen(LOOKUP_URL + urlencode(opts))
        results = fb_resp.read()
        fb_resp.close()
    except urllib2.HTTPError:
        raise ValueError("The token was invalid or there was a problem" +\
                "connecting to facebook")
    return json.loads(results)

def get_networks(access_token, uid):
    LOOKUP_URL = "https://api.facebook.com/method/fql.query?"
    opts = {'query':"SELECT affiliations FROM user WHERE uid=%s"%uid,
            'access_token':access_token, 'format':'json'}
    try:
        fb_resp = urllib2.urlopen(LOOKUP_URL + urlencode(opts))
        results = fb_resp.read()
        fb_resp.close()
    except urllib2.HTTPError:
        raise ValueError("The token was invalid or there was a problem" +\
                "connecting to facebook")
    return json.loads(results).get('affiliations', [])

def get_userid(code):
    acc_tok = get_access_token(code)
    info = get_basic_info(acc_tok)
    return info['id']

def redirect_to_fb_url():
    base_url = "https://www.facebook.com/dialog/oauth?"
    opts = {'client_id':settings.FB_APP_ID,
            'redirect_uri':settings.FB_REDIRECT_URL,
            'scope':'email',}
    return base_url + urlencode(opts)
