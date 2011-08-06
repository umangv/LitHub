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

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, redirect

from fbconnect.models import FBProfile
import fbconnect.utils as fb_utils

def receive_code(request):
    code = request.GET.get('code', '')
    if code:
        try:
            user = authenticate(fb_code=code)
            if user and user.is_active:
                login(request, user)
                return redirect('bookswap.views.my_account')
            else:
                return redirect('fbconnect.views.register', code=code)
        except ValueError:
            return render(request, "fbconnect/code_error.html")
    else:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('django.contrib.auth.views.login')

def register(request, code):
    return render(request, "fbconnect/register.html")

def redirect_to_fb(request):
    return redirect(fb_utils.redirect_to_fb_url())

def assoc_with_curr_user(request):
    code = request.GET.get('code', '')
    if code:
        try:
            uid = fb_utils.get_userid(code, assoc_with_curr_user)
            matches = FBProfile.objects.filter(fb_userid=uid).count()
            if matches:
                messages.error(request, "This facebook is already " +\
                        "associated with an account on LitHub")
                return redirect('bookswap.views.my_account')
            try:
                profile = FBProfile.objects.get(user=request.user)
            except ObjectDoesNotExist:
                profile = FBProfile(user=request.user)
            profile.fb_userid = uid
            profile.save()
            messages.success(request, "LitHub now recognizes your " +\
                    "facebook account.")
            return redirect('bookswap.views.my_account')
        except ValueError:
            return render(request, "fbconnect/code_error.html")
    else:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('django.contrib.auth.views.login')

def assoc_with_curr_user_redir(request):
    return redirect(fb_utils.redirect_to_fb_url(assoc_with_curr_user))
