# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import os
import re
import hashlib


def tokenize(value, tokens, remain=False):
    tokens = tokens.split('|')
    # tokenize with tokens
    rep = '<**>'
    if remain is False:  # remove tokens
        for v in tokens:
            value = value.replace(v, rep)
        temp = value.split(rep)
    elif remain is True:  # remain tokens
        for v in tokens:
            value = value.replace(v, rep + v + rep)
        temp = value.split(rep)
    return [v for v in temp if v is not '']


def mreplace(value, dictionary, wordbase=True,
             caseignore=True, tokens=' |_|.|(|)|[|]'):
    # dictionary2srcdst str
    if isinstance(dictionary, str):
        if '<' in dictionary:
            dst, srclist = dictionary.split('<')
        elif '>' in dictionary:
            srclist, dst = dictionary.split('>')
        srclist = srclist.split('|')

    def jointhandler(strlist, srclist, dst, tokens, caseignore=True):
        # try matching with joint character neighbored string
        for src in srclist:
            for token in tokens.split(u'|'):
                if token in src:
                    srcx = tokenize(src, tokens, remain=True)
                    for cnt in range(0, len(strlist) - len(srcx) + 1):
                        strm = ''.join(strlist[cnt:cnt + len(srcx)])
                        if caseignore is False:
                            if strm == src:
                                strlist[cnt] = dst
                                strlist[cnt + 1:cnt + len(srcx)] = ''
                        elif caseignore is True:
                            if strm.lower() == src.lower():
                                strlist[cnt] = dst
                                strlist[cnt + 1:cnt + len(srcx)] = ''
        return strlist

    # non wordbase replace
    if wordbase is False:
        if caseignore is False:
            for src in srclist:
                regexp = re.compile(re.escape(src))
                value = regexp.sub(dst, value)
        elif caseignore is True:
            for src in srclist:
                regexp = re.compile(re.escape(src), re.IGNORECASE)
                value = regexp.sub(dst, value)

    # wordbase replace
    elif wordbase is True:
        # tokens = u""" |_|.|(|)|[|]"""
        strlist = tokenize(value, tokens, remain=True)
        if caseignore is False:
            for cnt in range(0, len(strlist)):
                for src in srclist:
                    if strlist[cnt] == src:
                        strlist[cnt] = dst
            # consider joint character
            strlist = jointhandler(strlist, srclist,
                                   dst, tokens, caseignore=False)
        elif caseignore is True:
            for cnt in range(0, len(strlist)):
                for src in srclist:
                    if strlist[cnt].lower() == src.lower():
                        strlist[cnt] = dst
            # consider joint character
            strlist = jointhandler(strlist, srclist,
                                   dst, tokens, caseignore=True)
        value = u''.join(strlist)

    # remove doubled special character in neighbored dst
    # chars = u""" |_|.|,|`|'|"|-|+|=|~|!|?|(|)|[|]|@|#|$|%|^|&"""
    chars = '.'
    for this in chars.split('|'):
        if this in dst:
            value = value.replace(dst + this, dst)
    return value


class mstr(str):

    def __str__(self):
        return self

    def strpad(self, pad, num, reverse=False):
        value = self
        if reverse:
            for cnt in range(0, num - len(value)):
                value = value + pad
        else:
            for cnt in range(0, num - len(value)):
                value = pad + value
        return mstr(value)

    def tokenize(self, tokens, remain=False):
        return tokenize(self, tokens, remain=remain)

    def mstrip(self, pattern):
        value = self
        patterns = pattern.split('|')
        for i in range(len(patterns)):
            for v in patterns:
                value = value.strip(v)
        return mstr(value)

    def msplit(self, tokens):
        value = self
        rep = '<**>'
        for v in tokens.split('|'):
            value = value.replace(v, rep)
        return mstr([v for v in value.split(rep) if len(v) > 0])

    def mmreplace(self, dictionary, wordbase=True, caseignore=True):
        value = self
        for dc in dictionary.split('|'):
            value = mreplace(
                value, dc, wordbase=wordbase, caseignore=caseignore)
        return mstr(value)

    def mreplace(self, dictionary, wordbase=True,
                 caseignore=True, tokens=' |_|.|(|)|[|]'):
        value = mreplace(self, dictionary, wordbase=wordbase,
                         caseignore=caseignore, tokens=tokens)
        return mstr(value)

    def mcapitalize(self, patterns):
        value = self
        for v in patterns.split('|'):
            dc = '<'.join([v.upper(), v.lower()])
            value = mreplace(value, dc, wordbase=True, caseignore=True)
        return mstr(value)

    def get_pattern_index(self, pattern):
        match = re.search(pattern, self)
        index = []
        for match in re.finditer(pattern, self):
            s = match.start()
            e = match.end()
            index += [(s, e)]
            # print('Found "%s" at %d:%d' % (self[s:e], s, e))
        return index

    def get_pattern_index_from_to(self, pattern_from, pattern_to):
        index_from = self.get_pattern_index(pattern_from)
        index_to = self.get_pattern_index(pattern_to)
        index = []
        for s, e in index_from:
            v = [v for v in index_to if v[0] > e]
            if len(v) > 0:
                index += [((s, e), v)]
        return index

    def get_pattern_removed(self, pattern):
        value = self
        index = self.get_pattern_index(pattern)
        for s, e in index[::-1]:
            value = value[:s] + self[e:]
        return mstr(value)

    def insert(self, position, value, reverse=False):
        if reverse:
            position = len(self) - position
        if position < 0:
            position = 0
        if position > len(self):
            position = len(self)
        return mstr(self[:position] + value + self[position:])

    def get_hash_tags(self):
        index = self.get_pattern_index(r'[#]{1}[\w]{1,}')
        return [mstr(self[i[0] + 1:i[-1]]) for i in index]

    def get_alpha_tags(self):
        index = self.get_pattern_index(r'[@]{1}[\w]{1,}')
        return [mstr(self[i[0] + 1:i[-1]]) for i in index]

    def get_hash(self, algorithm):
        h = hashlib.new(algorithm)
        h.update(self.encode('utf-8'))
        return mstr(h.hexdigest())

    def get_md5(self):
        h = hashlib.md5()
        h.update(self.encode('utf-8'))
        return mstr(h.hexdigest())

    def get_sha256(self):
        h = hashlib.sha256()
        h.update(self.encode('utf-8'))
        return mstr(h.hexdigest())

    def get_sha512(self):
        h = hashlib.sha512()
        h.update(self.encode('utf-8'))
        return mstr(h.hexdigest())

    def guess_datetime(self):
        from datetime import datetime
        sp = '_| |.|,|-'
        ymd_template = r'[\d]{4}[%s]{0,1}[\d]{2}[%s]{0,1}[\d]{2}' % (sp, sp)
        hms_template = r'[\d]{2}[%s]{0,1}[\d]{2}[%s]{0,1}[\d]{2}' % (sp, sp)
        index = self.get_pattern_index(
            ymd_template + '[%s]{0,1}' % (sp) + hms_template)
        for idx in index:
            try:
                trial = ''.join(mstr(self[idx[0]:idx[1]]).msplit(sp))
                return mstr(datetime.strptime(trial, '%Y%m%d%H%M%S'))
            except:
                continue
        index = self.get_pattern_index(ymd_template)
        for idx in index:
            try:
                trial = ''.join(mstr(self[idx[0]:idx[1]]).msplit(sp))
                return mstr(datetime.strptime(trial, '%Y%m%d'))
            except:
                continue

    def month_to_digit(self):
        value = self
        dcs = ('01<jan|january', '02<feb|february', '03<mar|march',
               '04<apr|april', '05<may', '06<jun|june',
               '07<jul|july', '08<aug|august', '09<sep|september',
               '10<oct|october', '11<nov|november', '12<dec|december',)
        for dc in dcs:
            value = mreplace(value, dc)
        return mstr(value)

    def week_to_digit(self):
        value = self
        dcs = ('01<mon|monday', '02<tue|tuesday', '03<wed|wednesday',
               '04<thu|thursday', '05<fri|friday', '06<sat|saturday', '07<sun|sunday',)
        for dc in dcs:
            value = mreplace(value, dc)
        return mstr(value)

    def ymd_to_digit(self):
        value = self

        def is_valid_ymd(year, month, date=0):
            if month is None:
                return False
            if month.isdigit() is False:
                month = mstr(month).month_to_digit()
            if int(date) > 31:
                return False
            if int(month) > 12:
                return False
            if int(year) < 1950:
                return False
            if int(year) > 2020:
                return False
            return True

        dig2 = r'[0-9]{2}'
        dig4 = r'[0-9]{4}'
        char = r'[a-zA-Z]{3,9}'
        # x = r'[\s|\_|\.|\-|\+|\=|\(|\)|\[|\]|\{|\}|\'|\`]{1,}'
        x = r'[\s|\_|\.|\-|\(|\)|\[|\]|\{|\}]{1}'

        # 10 31 2014
        src = r'\A(.*)(%s)(%s)%s(%s)%s(%s)(.*)\Z' % (x, dig2, x, dig2, x, dig4)
        regexp = re.compile(src, re.IGNORECASE)
        m = regexp.match(value)
        if m is not None:
            g = list(m.groups())
            year, date, month = (g.pop(4), g.pop(3), g.pop(2))
            if is_valid_ymd(year, month, date):
                g.insert(2, year + month + date)
                value = ''.join(g)

        # 31 10 2014
        src = r'\A(.*)(%s)(%s)%s(%s)%s(%s)(.*)\Z' % (x, dig2, x, dig2, x, dig4)
        regexp = re.compile(src, re.IGNORECASE)
        m = regexp.match(value)
        if m is not None:
            g = list(m.groups())
            year, month, date = (g.pop(4), g.pop(3), g.pop(2))
            if is_valid_ymd(year, month, date):
                g.insert(2, year + month + date)
                value = ''.join(g)

        # 2014 10 10
        src = r'\A(.*)(%s)(%s)%s(%s)%s(%s)(.*)\Z' % (x, dig4, x, dig2, x, dig2)
        regexp = re.compile(src, re.IGNORECASE)
        m = regexp.match(value)
        if m is not None:
            g = list(m.groups())
            date, month, year = (g.pop(4), g.pop(3), g.pop(2))
            if is_valid_ymd(year, month, date):
                g.insert(2, year + month + date)
                value = ''.join(g)

        # May 10 2014
        src = r'\A(.*)(%s)(%s)%s(%s)%s(%s)(.*)\Z' % (x, char, x, dig2, x, dig4)
        regexp = re.compile(src, re.IGNORECASE)
        m = regexp.match(value)
        if m is not None:
            g = list(m.groups())
            year, date, month = (g.pop(4), g.pop(
                3), mstr(g.pop(2)).month_to_digit())
            if is_valid_ymd(year, month, date):
                g.insert(2, year + month + date)
                value = ''.join(g)

        # 10 May 2014
        src = r'\A(.*)(%s)(%s)%s(%s)%s(%s)(.*)\Z' % (x, dig2, x, char, x, dig4)
        regexp = re.compile(src, re.IGNORECASE)
        m = regexp.match(value)
        if m is not None:
            g = list(m.groups())
            year, month, date = (
                g.pop(4), mstr(g.pop(3)).month_to_digit(), g.pop(2))
            if is_valid_ymd(year, month, date):
                g.insert(2, year + month + date)
                value = ''.join(g)

        # May 2014
        src = r'\A(.*)(%s)(%s)%s(%s)(.*)\Z' % (x, char, x, dig4)
        regexp = re.compile(src, re.IGNORECASE)
        m = regexp.match(value)
        if m is not None:
            g = list(m.groups())
            year, month = (g.pop(3), mstr(g.pop(2)).month_to_digit())
            if is_valid_ymd(year, month):
                g.insert(2, year + month)
                value = ''.join(g)

        return value

    def place_dot_between(self):
        '''
        S.O.S (S.O.S) < S O S (S O S)
        '''
        value = ' ' + self + ' '
        x = r'[\s|\.|\(|\)]{1}'
        char = r'[a-zA-Z]{1}'
        src = r'\A(.*)(%s)(%s)([\s]{1})(%s)(%s)(.*)\Z' % (x, char, char, x)
        regexp = re.compile(src, re.IGNORECASE)
        for i in range(len(value)):
            m = regexp.match(value)
            if m is None:
                break
            g = list(m.groups())
            g[3] = '.'
            value = ''.join(g)
        return mstr(value[1:-1])

    def auto_bracket(self):
        value = self.close_bracket_head()
        return mstr(value.close_bracket_tail())

    def close_bracket_head(self):
        '''
        열림 괄호가 없고 닫힘 괄호만 있는 경우, 열림 괄호를 추가.
        (Python) < Python)
        '''
        brackets = (('(', ')'), ('{', '}'), ('[', ']'),)
        tokens = '|'.join(['|'.join(v) for v in brackets])
        strlist = tokenize(self, tokens, remain=True)
        for v in strlist:
            if v in '([{':
                return mstr(self)
            for bs in brackets:
                if v == bs[1]:
                    return mstr(bs[0] + self)
        return mstr(self)

    def close_bracket_tail(self):
        '''
        열림 괄호만 있고 닫힘 괄호가 없는 경우, 닫힘 괄호를 추가.
        (Python) < (Python
        '''
        brackets = (('(', ')'), ('{', '}'), ('[', ']'),)
        tokens = '|'.join(['|'.join(v) for v in brackets])
        strlist = tokenize(self, tokens, remain=True)
        for v in strlist[::-1]:
            if v in ')]}':
                return mstr(self)
            for bs in brackets:
                if v == bs[0]:
                    return mstr(self + bs[1])
        return mstr(self)

    def lower_after_wordbase(self, keywords):
        sp = ' |.|_|-|+|(|)|[|]|{|}'
        tokens = '|'.join([sp, keywords])
        keywords = keywords.split('|')
        parts = tokenize(self, tokens, remain=True)
        for i in range(1, len(parts), 1):
            for v in keywords:
                if v == parts[i - 1]:
                    parts[i] = parts[i].lower()
        return mstr(''.join(parts))

    def remove_after(self, keywords):
        value = self
        for v in keywords.split('|'):
            i = value.lower().find(v.lower())
            if i == -1:
                continue
            value = value[:i + len(v) + 1]
        return mstr(value)

    def has_in_string(self, words, caseignore=False):
        value = self
        if caseignore:
            words = words.lower()
            value = value.lower()
        for v in words.split('|'):
            if v in value:
                return True
        return False

    def get_path_split(self, depth=0):

        def split_dir(dirname):
            dirname = os.path.dirname(dirname)
            basename = os.path.basename(dirname)
            return dirname, basename

        dirbase = self
        elements = []
        for i in range(depth):
            dirbase, basename = split_dir(dirbase)
            elements.insert(0, basename)
        elements.insert(0, split_dir(dirbase)[0])
        elements = [v for v in elements if len(v) > 0]
        filename = os.path.basename(self)
        basename, extension = os.path.splitext(filename)
        elements += [basename, extension]
        return elements


def __test__():

    pad = 40
    value = ('Python is a) jan FEB 2016-05-05 (O K) '
             'multi-paradigm @peppy #language.')
    value = mstr(value)
    print('mstr()'.ljust(pad), value)

    print('-' * 120)

    print('mstr().get_pattern_index()'.ljust(pad),
          value.get_pattern_index('multi'))

    print('mstr().get_pattern_index_from_to()'.ljust(pad),
          value.get_pattern_index_from_to('multi', 'uage'))

    print('mstr().get_pattern_removed()'.ljust(pad),
          value.get_pattern_removed('multi'))

    print('-' * 120)

    tokens = '-'
    print('mstr().tokenize()'.ljust(pad),
          value.tokenize(tokens, remain=True))

    tokens = ' |-| a '
    print('mstr().msplit()'.ljust(pad),
          value.msplit(tokens))

    tokens = ' |.|Python'
    print('mstr().mstrip()'.ljust(pad),
          value.mstrip(tokens))

    dictionary = 'not a<a|multi'
    print('mstr().mreplace()'.ljust(pad),
          value.mreplace(dictionary))

    dictionary = 'not a<a|Java<Python'
    print('mstr().mmreplace()'.ljust(pad),
          value.mmreplace(dictionary))

    dictionary = 'a|is'
    print('mstr().mcapitalize()'.ljust(pad),
          value.mcapitalize(dictionary))

    print('-' * 120)

    print('mstr().insert()'.ljust(pad),
          value.insert(10, 'INSERTED '))

    print('mstr().auto_bracket()'.ljust(pad),
          value.auto_bracket())

    print('mstr().remove_after()'.ljust(pad),
          value.remove_after('multi'))

    print('mstr().place_dot_between()'.ljust(pad),
          value.place_dot_between())

    print('mstr().lower_after_wordbase()'.ljust(pad),
          value.lower_after_wordbase('F'))

    print('-' * 120)

    print('mstr().get_alpha_tags()'.ljust(pad),
          value.get_alpha_tags())

    print('mstr().get_hash_tags()'.ljust(pad),
          value.get_hash_tags())

    print('mstr().guess_datetime()'.ljust(pad),
          value.guess_datetime())

    print('mstr().ymd_to_digit()'.ljust(pad),
          value.ymd_to_digit())

    print('mstr().month_to_digit()'.ljust(pad),
          value.month_to_digit())

    print('mstr().week_to_digit()'.ljust(pad),
          value.week_to_digit())

    print('-' * 120)

    print('mstr().get_md5()'.ljust(pad),
          value.get_md5())

    print('mstr().get_sha256()'.ljust(pad),
          value.get_sha256())

    print('-' * 120)

    value = ('/var/www/project/0000/0001/image.png')
    value = mstr(value)
    print('mstr()'.ljust(pad), value)

    print('-' * 120)

    print('mstr().get_path_split()'.ljust(pad),
          value.get_path_split())

    print('mstr().get_path_split()'.ljust(pad),
          value.get_path_split(2))

    print('mstr().get_path_split()'.ljust(pad),
          value.get_path_split(10))

    print('-' * 120)

if __name__ == '__main__':
    __test__()
