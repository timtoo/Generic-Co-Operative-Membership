# Generic Co-operative Membership System.
# Copyright 2011 Tim Middleton
#
# Generic Co-operative Membership System is free software: you can
# redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Generic Co-operative Membership System is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Generic Co-operative Membership System.  If not, see
# <http://www.gnu.org/licenses/>.

import random
from itertools import izip
from django.db import connection

def queryDict(query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """
    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return


def query(query_string, *query_args):
    """Simple SQL query, returning list of tuples"""
    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    return cursor.fetchall()


def passgen(maxlen=12, mixed=False):
    """Generate a random quasi-pronouncable password"""
    const = 'bcdfghjklmnpqrstvwxyz'
    vowel = 'aeiouy'
    numeric = '1234567890'
    pairs = { 'b': 'lr',
              'c': 'chklr',
              'd': 'drw',
              'f': 'flr',
              'g': 'hlrn',
              'k': 'lr',
              'm': 'n',
              'p': 'hlpr',
              'q': 'u',
              'r': 'hl',
              's': 'chlnprtvw',
              't': 'hrwt',
              'a': 'ei',
              'e': 'ai',
              'i': 'eo',
              'o': 'eo',
            }
    alphanum = {
                'a': '4',
                'b': '6',
                'e': '3',
                'g': '9',
                'i': '1',
                'l': '1',
                'o': '0',
                's': '5',
                't': '7',
                'z': '2',
            }

    letters = const + vowel
    if mixed:
        const_full = const + const.upper()
        vowel_full = vowel + vowel.upper()
        letters_full = const_full + vowel_full
    else:
        const_full = const + const
        vowel_full = vowel + vowel
        letters_full = const_full + vowel_full

    def is_vowel(l):
        return l in vowel_full

    def is_const(l):
        return l in const_full

    def filter_char(l, one_in=5):
        ret = alphanum.get(l.lower())
        if ret is not None:
            if random.randint(1,one_in) == 1:
                l = ret
        return l

    def initial():
        return random.choice(letters_full)

    def next(last):
        last = last.lower()
        if is_vowel(last):
            charset = const_full
        else:
            charset = vowel_full

        if pairs.has_key(last):
            if mixed:
                charset += pairs[last] + pairs[last].upper()
            else:
                charset += pairs[last] + pairs[last]

        return random.choice(charset)


    def passchunk(maxlen):
        last_char = initial()
        pw = [ filter_char(last_char) ]

        while len(pw) < maxlen:
            last_char = next(last_char)
            pw.append(filter_char(last_char))

        return ''.join(pw)

    pw = ''
    while len(pw) < maxlen:
        chunklen = random.randint(4,7)
        pw += passchunk(chunklen)
    return pw[:maxlen]

