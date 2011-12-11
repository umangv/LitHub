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

from django.utils.http import urlencode
from django.conf import settings
from django.core.urlresolvers import reverse

import urllib2
from urlparse import parse_qs
import json

def lazy_prop(func):
    """Wrapper for properties that should be evaluated lazily

    This calls the actual method only once per instance. On the first time 
    the property is read, it's value is stored in self.__dict__.  The next
    time onwards, the stored value is returned. 

    Note that this wrapper also wraps the property wrapper on the method, so
    only the @lazy_prop wrapper needs to be used. 
    """
    def wrap(self, *args, **kwargs):
        if not func.__name__ in self.__dict__:
            self.__dict__[func.__name__] = func(self, *args, **kwargs)
        return self.__dict__[func.__name__]
    return property(wrap)

class FBConnect(object):
    """Access and run queries using the Facebook Connect API"""
    def __init__(self, code=None, view=None, access_token=None):
        if code != None:
            self.access_token = ""
            self._get_access_token(code, view)
        elif access_token != None:
            self.access_token = access_token
        elif access_token==None and code==None:
            raise ValueError('code and access_token cannot both be None.')

    def _get_access_token(self, code, view=None):
        LOOKUP_URL = "https://graph.facebook.com/oauth/access_token?"
        opts = {'client_id':settings.FB_APP_ID,
                'redirect_uri':_url_receiving_code(view),
                'client_secret':settings.FB_APP_SECRET,
                'code':code}
        try:
            fb_resp = urllib2.urlopen(LOOKUP_URL + urlencode(opts))
            result = fb_resp.read()
            fb_resp.close()
        except urllib2.HTTPError:
            raise ValueError("The code was invalid or there was a problem" \
            + " connecting to Facebook")
        resp = parse_qs(result)
        if not resp.has_key('access_token'):
            raise ValueError("No access token returned")
        self.access_token = resp['access_token'][0]

    @lazy_prop
    def basic_info(self):
        LOOKUP_URL = "https://graph.facebook.com/me?"
        opts = {'access_token':self.access_token,}
        try:
            fb_resp = urllib2.urlopen(LOOKUP_URL + urlencode(opts))
            results = fb_resp.read()
            fb_resp.close()
        except urllib2.HTTPError:
            raise ValueError("The token was invalid or there was a " +\
                    "problem connecting to facebook")
        return json.loads(results)

    @lazy_prop
    def networks(self):
        LOOKUP_URL = "https://api.facebook.com/method/fql.query?"
        opts = {'query':"SELECT affiliations FROM user WHERE uid=%s"%\
                self.userid, 'access_token':self.access_token,
                'format':'json'}
        try:
            fb_resp = urllib2.urlopen(LOOKUP_URL + urlencode(opts))
            results = fb_resp.read()
            fb_resp.close()
        except urllib2.HTTPError:
            raise ValueError("The token was invalid or there was a" + \
                    "problem connecting to facebook")
        return json.loads(results)[0]['affiliations']

    @lazy_prop
    def userid(self):
        return self.basic_info['id']

    def publish_og(self, action, obj_type, obj, params=None):
        opts = {'access_token':self.access_token,
            obj_type:obj}
        if params:
            opts.update(params)
            # Allows overriding any of the options in opts
        try:
            fb_resp = urllib2.urlopen(\
                    'https://graph.facebook.com/me/%s:%s'%(\
                    settings.FB_APP_NAMESPACE, action),
                    urlencode(opts))
            id = fb_resp.read()
            fb_resp.close()
        except urllib2.HTTPError as e:
            raise ValueError("There was a problem connecting to facebook.")
        return id

def _url_receiving_code(view=None):
    view = view or 'fbconnect.views.receive_code'
    extra = reverse(view)
    return settings.FB_REDIRECT_URL + extra

def redirect_to_fb_url(view=None):
    base_url = "https://www.facebook.com/dialog/oauth?"
    opts = {'client_id':settings.FB_APP_ID,
            'redirect_uri':_url_receiving_code(view),
            'scope':'email,publish_actions',}
    return base_url + urlencode(opts)
