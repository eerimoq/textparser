# A text parser.

from collections import namedtuple


__author__ = 'Erik Moqvist'
__version__ = '0.5.0'


class _Tokens(object):

    def __init__(self, tokens):
        if len(tokens) == 0 or tokens[-1].kind != '__EOF__':
            tokens.append(Token('__EOF__', None, None, None))

        self._tokens = tokens
        self._pos = 0
        self._stack = []

    def get(self):
        pos = self._pos
        self._pos += 1

        return self._tokens[pos]

    def peek(self):
        return self._tokens[self._pos]

    def save(self):
        self._stack.append(self._pos)

    def restore(self):
        self._pos = self._stack.pop()

    def drop(self):
        self._stack.pop()

    def __repr__(self):
        return str(self._tokens[self._pos:self._pos + 2])


class _String(object):
    """Matches a specific token kind.

    """

    def __init__(self, kind):
        self.kind = kind

    def match(self, tokens):
        if self.kind == tokens.peek().kind:
            return tokens.get().value
        else:
            return None


def _wrap_string(item):
    if isinstance(item, str):
        item = _String(item)

    return item


def _wrap_strings(items):
    return [_wrap_string(item) for item in items]


class Error(Exception):
    pass


class TokenizeError(Error):

    def __init__(self, line, column, offset, string):
        message = 'Invalid syntax at line {}, column {}: "{}"'.format(
            line,
            column,
            markup_line(string, offset))
        super(TokenizeError, self).__init__(message)
        self.line = line
        self.column = column
        self.offset = offset
        self.string = string


Token = namedtuple('Token', ['kind', 'value', 'line', 'column'])


class Sequence(object):
    """Matches a sequence of patterns.

    """

    def __init__(self, *members):
        self.members = _wrap_strings(members)

    def match(self, tokens):
        matched = []

        for member in self.members:
            mo = member.match(tokens)

            if mo is None:
                return None

            if isinstance(member, Inline) and isinstance(mo, list):
                matched.extend(mo)
            else:
                matched.append(mo)

        return matched


class Choice(object):
    """Matches any of given patterns.

    """

    def __init__(self, *members):
        self._members = _wrap_strings(members)

    def match(self, tokens):
        for member in self._members:
            tokens.save()
            mo = member.match(tokens)

            if mo is not None:
                tokens.drop()

                return mo

            tokens.restore()

        return None


class ChoiceDict(object):
    """Matches any of given patterns.

    """

    def __init__(self, *members):
        self._members_map = {}
        members = _wrap_strings(members)

        for member in members:
            if isinstance(member, _String):
                if member.kind in self._members_map:
                    raise Error

                self._members_map[member.kind] = member
            else:
                if not isinstance(member, Sequence):
                    raise Error

                if not isinstance(member.members[0], _String):
                    raise Error

                if member.members[0].kind in self._members_map:
                    raise Error

                self._members_map[member.members[0].kind] = member

    def match(self, tokens):
        kind = tokens.peek().kind

        if kind in self._members_map:
            return self._members_map[kind].match(tokens)
        else:
            return None


class ZeroOrMore(object):
    """Matches a pattern zero or more times.

    """

    def __init__(self, element, end=None):
        self._element = _wrap_string(element)

        if end is not None:
            end = _wrap_string(end)

        self._end = end

    def match(self, tokens):
        matched = []

        while True:
            if self._end is not None:
                tokens.save()
                mo = self._end.match(tokens)
                tokens.restore()

                if mo is not None:
                    break

            mo = self._element.match(tokens)

            if mo is None:
                break

            matched.append(mo)

        return matched


class OneOrMore(object):
    """Matches a pattern one or more times.

    """

    def __init__(self, element, end=None):
        self._element = _wrap_string(element)

        if end is not None:
            end = _wrap_string(end)

        self._end = end

    def match(self, tokens):
        matched = []

        while True:
            if self._end is not None:
                tokens.save()
                mo = self._end.match(tokens)
                tokens.restore()

                if mo is not None:
                    break

            mo = self._element.match(tokens)

            if mo is None:
                break

            matched.append(mo)

        if len(matched) > 0:
            return matched
        else:
            return None


class Any(object):
    """Matches any token.

    """

    def match(self, tokens):
        return tokens.get().value


class DelimitedList(object):
    """Matches a delimented list of given pattern.

    """

    def __init__(self, element, delim=','):
        self._element = _wrap_string(element)
        self._delim = _wrap_string(delim)

    def match(self, tokens):
        matched = []

        while True:
            # Element.
            mo = self._element.match(tokens)

            if mo is None:
                return None

            matched.append(mo)

            # Delimiter.
            mo = self._delim.match(tokens)

            if mo is None:
                return matched


class Inline(object):

    def __init__(self, element):
        self._element = element

    def match(self, tokens):
        return self._element.match(tokens)


class Optional(object):
    """Matches a pattern zero or one times.

    """

    def __init__(self, element):
        self._element = _wrap_string(element)

    def match(self, tokens):
        mo = self._element.match(tokens)

        if mo is None:
            return []
        else:
            return [mo]


class Forward(object):

    def __init__(self):
        self._inner = None

    def __ilshift__(self, other):
        self._inner = other

        return self

    def match(self, tokens):
        return self._inner.match(tokens)


class Grammar(object):
    """Creates a tree of given tokens.

    """

    def __init__(self, grammar):
        self._root = grammar

    def parse(self, tokens):
        tokens = _Tokens(tokens)
        parsed = self._root.match(tokens)

        if parsed is not None and tokens.get().kind == '__EOF__':
            return parsed
        else:
            raise Error


def choice(*members):
    try:
        return ChoiceDict(*members)
    except Error:
        return Choice(*members)


def markup_line(string, offset):
    begin = string.rfind('\n', 0, offset)
    begin += 1

    end = string.find('\n', offset)

    if end == -1:
        end = len(string)

    return string[begin:offset] + '>>!<<' + string[offset:end]


def tokenize_init(spec):
    line = 1
    line_start = -1
    tokens = []
    re_token = '|'.join([
        '(?P<{}>{})'.format(name, regex) for name, regex in spec
    ])

    return line, line_start, tokens, re_token
