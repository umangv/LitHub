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

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns('fbconnect.views',
    url(r'^$', 'receive_code'), 
    url(r'^register/(?P<code>[^\\]+)/$', 'register'), 
    url(r'^redirect/$', 'redirect_to_fb'), 
    url(r'^assoc_curr/redirect/$', 'assoc_with_curr_user_redir'), 
    url(r'^assoc_curr/$', 'assoc_with_curr_user'), 
    url(r'^change_pass/redirect/$', 'change_pass_redir'), 
    url(r'^change_pass/$', 'change_pass'), 
    url(r'^privacy/$', TemplateView.as_view(
        template_name="fbconnect/privacy.html"), name="fbconnect_privacy"), 
)
