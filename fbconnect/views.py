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
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect

import urlparse
from uuid import uuid4

from fbconnect.models import FBProfile
import fbconnect.utils as fb_utils
from fbconnect.forms import FBRegisterForm, FBRegisterVerifyForm

def receive_code(request):
    """Receives fb code for logging in."""
    try:
        code = request.GET.get('code', '')
        fb = fb_utils.FBConnect(code)
        user = authenticate(fb_uid=fb.userid)
        if user and user.is_active:
            login(request, user)
            request.session['fb_at'] = fb.access_token
            next = request.session.get('next', '')
            try:
                del request.session['next']
            except KeyError:
                pass
            netloc = urlparse.urlparse(next)[1]
            # Security check: taken from Django code in
            # django.contrib.auth.views.login 
            # (don't allow redirection to different host)
            if netloc and netloc != request.get_host():
                next = ''
            # Ensure that Django doesn't URL reverse.
            if next and next[0] == '/':
                return HttpResponseRedirect(next)
            else:
                return redirect('bookswap.views.my_account')
        if user and not user.is_active:
            messages.error(request, "Please activate your account before "
                "you login. If you haven't received an email about this "
                "please contact us.")
            return redirect('bookswap.views.my_account')
        else:
            return redirect(register, access_token=fb.access_token)
    except ValueError:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('django.contrib.auth.views.login')

def register(request, access_token):
    try:
        fb = fb_utils.FBConnect(access_token=access_token)
        user = authenticate(fb_uid=fb.userid)
        if user:
            return redirect("bookswap.views.my_account")
        networks = fb.networks
        k = False
        for network in networks:
            if str(network['nid']) == '16777626':
                k = True
                break
        if k:
            createform = FBRegisterForm()
        else:
            createform = FBRegisterVerifyForm()
        loginform = AuthenticationForm()
        if request.method == 'POST':
            action = request.POST.get('action', '')
            if k and action == "createnew":
                createform = FBRegisterForm(request.POST)
                if createform.is_valid():
                    user_info = fb.basic_info
                    new_user = User.objects.create_user(
                            createform.cleaned_data['username'], 
                            user_info['email'])
                    new_user.first_name = user_info['first_name']
                    new_user.last_name = user_info['last_name']
                    new_user.is_active = True
                    new_user.set_unusable_password()
                    new_user.save()
                    fbp = FBProfile(user=new_user, fb_userid=user_info['id'])
                    fbp.save()
                    messages.success(request, "Your account has been created!")
                    user = authenticate(fb_uid=fbp.fb_userid)
                    request.session['fb_at'] = fb.access_token
                    if user and user.is_active:
                        login(request, user)
                    return redirect('bookswap.views.my_account')
            if (not k) and action == "createnew":
                createform = FBRegisterVerifyForm(request.POST)
                if createform.is_valid():
                    from bookswap.kregform import KzooRegistrationBackend
                    user_info = fb.basic_info
                    backend = KzooRegistrationBackend()
                    new_user = backend.register(request,
                            username=createform.cleaned_data['username'],
                            email=createform.cleaned_data['email'],
                            password1=None,
                            first_name=user_info['first_name'],
                            last_name=user_info['last_name'])
                    new_user.set_unusable_password()
                    new_user.save()
                    fbp = FBProfile(user=new_user, fb_userid=user_info['id'])
                    fbp.save()
                    messages.success(request, "An email has been sent to your "
                        "account. Once you confirm your account, you will be "
                        "able to log in.")
                    return redirect('bookswap.views.my_account')
            elif action == "associate":
                loginform = AuthenticationForm(data=request.POST)
                if loginform.is_valid():
                    user = loginform.get_user()
                    login(request, user)
                    try:
                        user.fbprofile
                        messages.error(request, "You are already connected to "
                            "a facebook account. If you are trying to connect "
                            "a different facebook account, please dissociate "
                            "your LitHub and facebook accounts.")
                        return redirect('bookswap.views.my_account')
                    except ObjectDoesNotExist:
                        pass 
                    fbp = FBProfile(user=user,fb_userid=fb.basic_info['id'])
                    fbp.save()
                    request.session['fb_at'] = fb.access_token
                    messages.success(request, "Your account is now connected "
                            "to your Facebook account!")
                    return redirect('bookswap.views.my_account')
        template = {True:"register.html", False:"register_verify.html"}
        return render(request, "fbconnect/%s"%template[k], 
                {'createform':createform, "loginform":loginform})
    except ValueError:
        return render(request, "fbconnect/code_error.html")

def redirect_to_fb(request):
    next = request.GET.get('next', '')
    netloc = urlparse.urlparse(next)[1]
    if netloc and netloc != request.get_host():
        next = ''
    if next and next[0] == '/':
        request.session['next'] = next
    return redirect(fb_utils.redirect_to_fb_url())

def assoc_with_curr_user(request):
    try:
        fb = fb_utils.FBConnect(request.GET.get('code', ''),
                assoc_with_curr_user)
        uid = fb.userid
        matches = FBProfile.objects.filter(fb_userid=uid).count()
        if matches:
            messages.error(request, "Your facebook account is already " +\
                    "associated with another account on LitHub")
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
        if request.method == "GET":
            fb = fb_utils.FBConnect(request.GET.get('code', ''), change_pass)
            if fb.userid != request.user.fbprofile.fb_userid:
                messages.error(request, "Your facebook account did not" +\
                    " match the one registered with LitHub.")
                return redirect('bookswap.views.my_account')
            request.session['fb_password_uuid'] = str(uuid4())
        form = SetPasswordForm(user=request.user)
        post_uuid = request.POST.get('uuid', '')
        if request.method=="POST" and  post_uuid and \
                post_uuid == request.session["fb_password_uuid"]:
            form = SetPasswordForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                request.session['fb_password_uuid'] = ""
                messages.success(request, "Your password was "+\
                    "successfully changed.")
                return redirect("bookswap.views.my_account")
        return render(request, "fbconnect/password_change.html",
                {'form':form, 'uuid':request.session["fb_password_uuid"]},)
    except ObjectDoesNotExist:
        messages.error(request, "Your facebook account was not recognized.")
    except ValueError:
        messages.error(request, "There was an error getting your " +\
            "information from facebook.")
    return redirect('bookswap.views.my_account')

def change_pass_redir(request):
    return redirect(fb_utils.redirect_to_fb_url(change_pass))
