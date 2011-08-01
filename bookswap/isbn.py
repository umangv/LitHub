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

def clean_isbn(isbn):
    """Returns a valid ISBN-13 or raises a ValueError"""
    try:
        isbn = str(isbn)
        isbn = isbn.replace(' ', '')
        isbn = isbn.replace('-', '')
        isbn = isbn.replace('.', '')
        if len(isbn) == 10: 
            if isbn[-1] == 'X':
                int(isbn[:-1])
            else:
                int(isbn)
            # i is the count, 0->10, x is the digit
            sum = 0
            for i, x in enumerate(isbn[:9]):
                sum += (i + 1) * int(x)
            sum = sum % 11
            if sum == 10 and isbn[9] != 'X':
                raise ValueError("Invalid ISBN")
            elif int(isbn[9]) != sum:
                raise ValueError("Invalid ISBN")
            return ten_to_thirteen(isbn)
        elif len(isbn) == 13:
            int(isbn)
            sum = 0
            weight = lambda x,y: x * [1,3][y%2]
            for i, x in enumerate(isbn[:12]):
                sum += weight(int(x), i)
            sum = sum % 10
            sum = 10 - sum
            sum = sum % 10
            if int(isbn[12]) != sum:
                raise ValueError("Invalid ISBN")
            return isbn
        else:
            raise ValueError("Invalid ISBN")
    except ValueError:
        raise ValueError("Invalid ISBN")

def ten_to_thirteen(isbn):
    """Converts a ISBN-10 to ISBN-13
    
    Note that this doesn't check if the ISBN-10 is valid. 
    clean_isbn performs that check before calling this function."""
    if len(isbn) == 10:
        isbn = "978" + isbn[:9]
        int(isbn)
        sum = 0
        weight = lambda x,y: x * [1,3][y%2]
        for i, x in enumerate(isbn[:12]):
            sum += weight(int(x), i)
        sum = sum % 10
        sum = 10 - sum
        sum = sum % 10
        return isbn + str(sum)
    else:
        raise ValueError("Invalid ISBN")
