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
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from fbconnect.models import FBProfile
import fbconnect.utils as fb_utils
from fbconnect.forms import FBRegisterForm

def receive_code(request):
    try:
        code = request.GET.get('code', '')
        fb = fb_utils.FBConnect(code)
        user = authenticate(fb_uid=fb.userid)
        if user and user.is_active:
            login(request, user)
            return redirect('bookswap.views.my_account')
        else:
            return redirect('fbconnect.views.register', code=code)
    except ValueError:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('django.contrib.auth.views.login')

def register(request, code):
    try:
        fb = fb_utils.FBConnect(code)
        networks = fb.networks
        k = False
        for network in networks:
            if str(network['nid']) == '16777626':
                k = True
                break
        if not k:
            messages.error(request, "You are not in the Kalamazoo "+\
                "College network on Facebook. Please join the " +\
                "Kalamazoo College Network and try again or register "+\
                "using the form below. You may connect your account " +\
                "to Facebook after registration")
            return redirect('registration.views.register')
        form = FBRegisterForm()
        if request.method == 'POST':
            form = FBRegisterForm(request.POST)
            if form.is_valid():
                user_info = fb.basic_info
                new_user = User.objects.create_user(
                        form.cleaned_data['username'], 
                        user_info['email'])
                new_user.first_name = user_info['first_name']
                new_user.last_name = user_info['last_name']
                new_user.is_active = True
                new_user.save()
                fbp = FBProfile(user=new_user, fb_userid=user_info['id'])
                fbp.save()
                messages.success(request, "Your account has been created!")
                user = authenticate(fb_uid=fbp.fb_userid)
                if user and user.is_active:
                    login(request, user)
                return redirect('bookswap.views.my_account')
        return render(request, "fbconnect/register.html", 
                {'form':form})
    except ValueError:
        return render(request, "fbconnect/code_error.html")

def redirect_to_fb(request):
    return redirect(fb_utils.redirect_to_fb_url())

def assoc_with_curr_user(request):
    try:
        fb = fb_utils.FBConnect(request.GET.get('code', ''),
                assoc_with_curr_user)
        uid = fb.userid
        matches = FBProfile.objects.filter(fb_userid=uid).count()
        if matches:
            messages.error(request, "Your facebook account is already " +\
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
    except ValueError:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('bookswap.views.my_account')

def assoc_with_curr_user_redir(request):
    return redirect(fb_utils.redirect_to_fb_url(assoc_with_curr_user))

def change_pass(request):
    try:
        fb = fb_utils.FBConnect(request.GET.get('code', ''), change_pass)
        if fb.userid != request.user.fbprofile.fb_userid:
            messages.error(request, "Your facebook account did not" +\
                " match the one registered with LitHub.")
            return redirect('bookswap.views.my_account')
        form = SetPasswordForm(user=request.user)
        if request.method=="POST":
            form = SetPasswordForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password was "+\
                    "successfully changed.")
                return redirect("bookswap.views.my_account")
        return render(request, "fbconnect/password_change.html",
                {'form':form},)
    except ObjectDoesNotExist:
        messages.error(request, "Your facebook account was not recognized.")
    except ValueError:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('bookswap.views.my_account')

def change_pass_redir(request):
    return redirect(fb_utils.redirect_to_fb_url(change_pass))
