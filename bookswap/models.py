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

from django.db import models
from django.contrib.auth.models import User

COPY_CONDITIONS = (('Like New', 'Like New'), ('Very Good', 'Very Good'), (
    'Good', 'Good'), ('Moderate', 'Moderate'), ('Bad', 'Bad'))

class Book(models.Model):
    isbn = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    copyrightYear=models.IntegerField(verbose_name="Copyright Year")
    publisher=models.CharField(max_length=100)
    thumbnail_url = models.CharField(max_length=500, blank=True)
    subscribers = models.ManyToManyField(User, related_name='subscriptions')

    def __unicode__(self):
        return "'%s' by '%s' (%d); %s"%(self.title, self.author,
                self.copyrightYear, self.isbn)

class Copy(models.Model):
    book = models.ForeignKey(Book)
    owner = models.ForeignKey(User)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(choices=COPY_CONDITIONS,
            max_length=10)
    pubDate = models.DateTimeField()
    comments = models.CharField(blank=True, null=True, max_length=200)
    soldTime = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s's copy of '%s'"%(self.owner.username, self.book.title)

    class Meta:
        verbose_name_plural = "Copies"

class Feedback(models.Model):
    name = models.CharField(max_length=30)
    subject = models.CharField(max_length=100)
    comment = models.TextField()
    date = models.DateTimeField()

    def __unicode__(self):
        return "%s's comments about '%s'"%(self.name, self.subject[:30])
