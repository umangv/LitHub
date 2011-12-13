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

from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change, \
        password_change_done, password_reset, password_reset_confirm, \
        password_reset_done, password_reset_complete
from django.views.generic import TemplateView
from render_template import render_template

urlpatterns = patterns('bookswap.views',
    (r'^bookswap/isbn/(?P<isbn_no>\w+)/$','book_by_isbn'),
    (r'^bookswap/book/(?P<book_id>\d+)/$','book_details'),
    (r'^bookswap/search_books/$', 'search_books'),
    (r'^bookswap/all_books/$', 'all_books'),
    (r'^bookswap/contact/$', 'contact_us'),
    (r'^bookswap/sell/search/$', 'sell_step_search'),
    (r'^bookswap/sell/existing/(?P<book_id>\d+)/$', 'sell_existing'),
    (r'^bookswap/sell/new/(?P<isbn_no>\d+)/$', 'sell_new'),
    (r'^bookswap/mark_sold/(?P<copy_id>\d+)/$', 'mark_sold'),
    (r'^bookswap/edit_copy/(?P<copy_id>\d+)/$', 'edit_copy'),
    (r'^bookswap/buy_copy/(?P<copy_id>\d+)/$', 'buy_copy'),
    (r'^bookswap/subscribe/(?P<book_id>\d+)/$', 'subscribe'),
    (r'^bookswap/unsubscribe/(?P<book_id>\d+)/$', 'unsubscribe'),
    (r'^bookswap/subscribe/new/(?P<isbn_no>\w+)/$', 'subscribed_to_new'),
    (r'^bookswap/publish/fb_list/(?P<copy_id>\d+)/$', 'fb_og_publish'),
    url(r'^accounts/logout/$', logout, name="logout"),
    url(r'^accounts/login/$', login, name="login"),
    url(r'^accounts/password/reset/$', 'password_reset_wrapper',
        name="password_reset"),
    url(r'^accounts/password/reset/done/$', password_reset_done),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>.*)/(?P<token>.*)/$',
        password_reset_confirm, name="password_reset_confirm"),
    url(r'^accounts/password/reset/complete/$', password_reset_complete),
    url(r'^accounts/change_password/$', 'password_change_wrapper',
        name="password_change"),
    (r'^accounts/change_password_done/$', password_change_done),
    (r'^accounts/profile/$', 'my_account'),
    (r'^accounts/profile/delete/$', 'delete_account'),
    (r'^accounts/profile/delete/success/$', 'delete_account_success'),
    (r'^accounts/profile/dissoc_fb/$', 'dissoc_fb'),
    (r'^accounts/profile/view/(?P<username>.+)/$', 'view_profile'),
    url(r'^$', render_template, {'template':"bookswap/home.html"},
        name="home"),
    )
