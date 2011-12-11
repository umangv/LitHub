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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as authViews
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext, Context, loader
from django.core.mail import send_mail
from django.conf import settings

from datetime import datetime
import utils
import isbn
from smtplib import SMTPException

from bookswap.models import Book, Copy
from bookswap.forms import *
from fbconnect import utils as fbutils

def render_403(error, status=403):
    t = loader.get_template('bookswap/error.html')
    c = Context({'error':error,})
    return HttpResponse(t.render(c), status=status)

def book_by_isbn(request, isbn_no):
    try:
        isbn_no = isbn.clean_isbn(isbn_no)
        books = Book.objects.filter(isbn=isbn_no)
        results = [(b, len(b.copy_set.all().filter(soldTime=None))) for b in books]
        results.sort(reverse=True, key=lambda x:x[1])
    except ValueError:
        results = []
    return render(request, "bookswap/book_isbn.html",
            {"results":results, 'search_isbn':isbn_no})

def book_details(request, book_id):
    book = Book.objects.get(pk=book_id)
    copies = book.copy_set.filter(soldTime=None).order_by('price')
    return render(request, "bookswap/book_copies.html",
        {"book":book, 'copies':copies, 'settings':settings})

def search_books(request):
    if request.method == "POST":
        if request.POST.get('action') == 'isbn_search':
            try:
                isbn_no = isbn.clean_isbn(request.POST.get("isbn","0"))
                return redirect(book_by_isbn, isbn_no=isbn_no)
            except ValueError:
                messages.error(request, "Please enter a valid ISBN number")
                return render(request, "bookswap/home.html",
                        {'search_isbn':request.POST.get('isbn','')})
    title = request.GET.get('title', '')
    author = request.GET.get('author', '')
    if title or author:
        books = Book.objects.filter(title__icontains=title,
                author__icontains=author)
        results = [(b, len(b.copy_set.filter(soldTime=None))) for b in books]
        results.sort(reverse=True, key=lambda x:x[1])
        return render(request, "bookswap/results.html",
                {"results":results, 'search_title':title,
                    'search_author':author})
    else:
        return redirect(all_books)

def all_books(request):
    books = Book.objects.all()
    results = [(b, len(b.copy_set.all().filter(soldTime=None))) for b in books]
    results.sort(reverse=True, key=lambda x:x[1])
    return render(request, "bookswap/all_books.html",
            {"results":results})

def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.date = datetime.now()
            feedback.save()
            messages.success(request, "Thank you for your feedback! We " +\
                    "appreciate your valuable input.")
            mail_body = ("Hi!\n\nKzoo Lithub received new feedback:\n\n" +\
                    "Name: %s\n\nSubject:%s\n\nComments:\n%s\n\n" +\
                    "With love from your sincere mail bot!")%( \
                    feedback.name, feedback.subject, feedback.comment)
            send_mail('New feedback received', mail_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False)
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, "bookswap/contact.html", {'form':form})

@login_required
def sell_step_search(request):
    """This step helps identify the book the user is trying to sell"""
    if request.method == "POST":
        isbn_no = request.POST.get('isbn', '')
        try:
            isbn_no = isbn.clean_isbn(isbn_no)
            books = Book.objects.filter(isbn=isbn_no)
            results = [(b, b.copy_set.filter(soldTime=None).count()) \
                    for b in books]
            if results:
                results.sort(reverse=True, key=lambda x:x[1])
                return render(request,
                    "bookswap/sell_select_book.html", 
                    {'results':results, 'isbn_no':isbn_no})
            else:
                return redirect('bookswap.views.sell_new', isbn_no)
        except ValueError:
            messages.error(request, "Invalid ISBN code")
    return render(request, "bookswap/sell_search.html")

@login_required
def sell_existing(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    form = SellExistingBookForm()
    if request.method == 'POST':
        form = SellExistingBookForm(request.POST)
        if form.is_valid():
            copy = form.save(commit=False)
            copy.book = book
            copy.owner = request.user
            copy.pubDate = datetime.now()
            copy.save()
            messages.success(request, "Your copy of `%s` is now on sale."%\
                    book.title)
            utils.opengraph_list_book(request, copy)
            return redirect('bookswap.views.book_details', book.id)
    return render(request, "bookswap/sell_existing.html",
            {'form':form, 'book':book})

@login_required
def sell_new(request, isbn_no):
    # If an exception is raised at this stage
    # it's not our responsibility to be nice. No well meaning
    # user will see an error page at this stage
    isbn_no = isbn.clean_isbn(isbn_no)
    info = utils.get_book_details(isbn_no)
    if request.method == 'POST':
        book_form = SellNewBookForm(request.POST, prefix="book")
        copy_form = SellExistingBookForm(request.POST, prefix="copy")
        if book_form.is_valid() and copy_form.is_valid():
            book = book_form.save(commit=False)
            book.isbn = isbn_no
            if info:
                book.thumbnail_url = info['thumbnail_url']
            book.save()
            copy = copy_form.save(commit=False)
            copy.book = book
            copy.owner = request.user
            copy.pubDate = datetime.now()
            copy.save()
            messages.success(request, "Your copy of `%s` is now on sale."%\
                    book.title)
            utils.opengraph_list_book(request, copy)
            return redirect('bookswap.views.book_details', book.id)
    else:
        book_form = SellNewBookForm(prefix="book", initial=info)
        copy_form = SellExistingBookForm(prefix="copy")
    return render(request, "bookswap/sell_new.html",
            {'book_form':book_form, 'copy_form':copy_form,
                'isbn_no':isbn_no})

@login_required
def my_account(request):
    copies = request.user.copy_set.filter(soldTime=None)
    try:
        request.user.fbprofile
        fb = True
    except ObjectDoesNotExist:
        fb = False
    return render(request, "bookswap/my_account.html",
            {'copies':copies, 'fb':fb})

@login_required
def mark_sold(request, copy_id):
    copy = Copy.objects.get(pk=copy_id)
    if copy.soldTime != None:
        messages.error(request, "This book is already sold!")
        return redirect('bookswap.views.my_account')
    if copy.owner != request.user:
        messages.error(request, "You may not sell this copy of " +\
                "the book. You do not own it.")
        return redirect('bookswap.views.my_account')
    if request.method == 'POST':
        copy.soldTime = datetime.now()
        copy.save()
        messages.success(request, "Your copy was successfully " +\
                "marked as sold. It will no longer be listed " +\
                "publicly on this website.")
        return redirect('bookswap.views.my_account')
    else:
        return render(request, "bookswap/mark_sold.html",
                {'copy':copy})

@login_required
def edit_copy(request, copy_id):
    copy = Copy.objects.get(pk=copy_id)
    if copy.soldTime != None:
        messages.error(request, "This book is already sold!")
        return redirect('bookswap.views.my_account')
    if copy.owner != request.user:
        messages.error(request, "You may not edit this copy." +\
                " You do not own it.")
        return redirect('bookswap.views.my_account')
    form = EditCopyForm(instance=copy)
    if request.method == 'POST':
        form = EditCopyForm(request.POST, instance=copy)
        if form.is_valid():
            copy = form.save()
            messages.success(request, "Your copy of `%s` was saved" %\
                    copy.book.title)
            return redirect('bookswap.views.my_account')
        else:
            messages.error(request, "There was an error in the form." +\
                    " Please fix the error and try again.")
    return render(request, "bookswap/edit_copy.html",
            {'form':form, 'copy':copy})

@login_required
def fb_og_publish(request, copy_id):
    copy = get_object_or_404(Copy, pk=copy_id)
    if copy.owner == request.user:
        publish = utils.opengraph_list_book(request, copy)
        if publish:
            messages.success(request, "Published to your facebook activity log")
        else:
            messages.error(request, "Error publishing to facebook. Try" +\
                    " logging in again.")
    return redirect(my_account)

@login_required
def view_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, "bookswap/profile_view.html",
            {'user':user})

@login_required
def buy_copy(request, copy_id):
    copy = get_object_or_404(Copy, pk=copy_id)
    if copy.soldTime != None:
        messages.error(request, "The copy you requested is no longer " +\
                "available.")
        return redirect(book_details, book_id=copy.book.id)
    if copy.owner == request.user:
        return redirect(book_details, book_id=copy.book.id)
    if request.method == 'POST':
        body = request.POST.get('emailbody', '')
        if not body:
            return redirect(buy_copy, copy_id=copy_id)
        email_body = loader.render_to_string('bookswap/buy_copy_email.html',
                {'copy':copy, 'buyer':request.user,
                    'site':settings.FB_REDIRECT_URL, 'body':body})
        subject = ('[Kzoo LitHub] %s wants to buy your book on ' +\
               'LitHub')%(request.user.username)
        email = EmailMessage(subject=subject, body=email_body,
                to=[copy.owner.email], cc=[request.user.email],
                headers={'Reply-To': request.user.email})
        try:
            email.send(fail_silently=False)
            messages.success(request, "Email sent successfully. You were " +\
                    "CC'ed and will receive a copy.")
            return redirect(book_details, book_id=copy.book.id)
        except SMTPException:
            messages.error(request, "There was an error sending the email." +\
                    "Please try again or contact the seller directly")
    return render(request, "bookswap/buy_copy.html", {'copy':copy})

def password_reset_wrapper(request, *args, **kwargs):
    from django.contrib.auth.views import password_reset
    if request.method == 'POST':
        users = User.objects.filter(
                email__iexact= request.POST.get('email', ''),
                is_active=True)
        if len(users):
            if any([not user.has_usable_password() for user in users]):
                return render(request,
                        "registration/password_reset_has_fb.html")
    return password_reset(request, *args, **kwargs)

@login_required
def password_change_wrapper(request, *args, **kwargs):
    from django.contrib.auth.views import password_change
    if not request.user.has_usable_password():
        return redirect('fbconnect.views.change_pass_redir')
    return password_change(request, *args, **kwargs)

@login_required
def delete_account(request):
    if request.method=='POST':
        password = request.POST.get('password', '')
        if request.user.check_password(password):
            request.user.delete()
            return redirect('bookswap.views.delete_account_success')
        else:
            messages.error(request, "Your password did not match")
    form = ConfirmPasswordForm()
    return render(request, "registration/delete_account.html",
            {'form':form})

def delete_account_success(request):
    return render(request, "registration/delete_account_success.html")

def dissoc_fb(request):
    try:
        request.user.fbprofile
    except ObjectDoesNotExist:
        messages.error(request, "Your account is not connected to a " +\
            "facebook profile.")
        return redirect(my_account)
    if request.method=='POST':
        password = request.POST.get('password', '')
        if request.user.check_password(password):
            request.user.fbprofile.delete()
            messages.success(request, "Your LitHub and facebook accounts"+\
                    " are no longer connected.")
            return redirect(my_account)
        else:
            messages.error(request, "Your password did not match")
    form = ConfirmPasswordForm()
    return render(request, "registration/dissoc_fb.html",
            {'form':form})
