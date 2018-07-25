# A text parser.

import re
from collections import namedtuple
from operator import itemgetter


__author__ = 'Erik Moqvist'
__version__ = '0.9.0'


class _Tokens(object):

    def __init__(self, tokens):
        if len(tokens) == 0 or tokens[-1].kind != '__EOF__':
            tokens.append(Token('__EOF__', None, -1))

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



def _format_invalid_syntax(string, offset):
    return 'Invalid syntax at line {}, column {}: "{}"'.format(
        line(string, offset),
        column(string, offset),
        markup_line(string, offset))


class TokenizeError(Error):

    def __init__(self, string, offset):
        self.string = string
        self.offset = offset
        message = _format_invalid_syntax(string, offset)
        super(TokenizeError, self).__init__(message)


class GrammarError(Error):

    def __init__(self, offset):
        self.offset = offset
        message = 'Invalid syntax at offset {}.'.format(offset)
        super(GrammarError, self).__init__(message)


class ParseError(Error):

    def __init__(self, string, offset):
        self.string = string
        self.offset = offset
        self.line = line(string, offset)
        self.column = column(string, offset)
        message = _format_invalid_syntax(string, offset)
        super(ParseError, self).__init__(message)


Token = namedtuple('Token', ['kind', 'value', 'offset'])


class Pattern(object):

    def match(self, tokens):
        raise NotImplementedError('To be implemented by subclasses.')


class Sequence(Pattern):
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


class Choice(Pattern):
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


class ChoiceDict(Pattern):
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


class Repeated(Pattern):
    """Matches a pattern zero or more times.

    """

    def __init__(self, element, end=None, minimum_length=0):
        self._element = _wrap_string(element)

        if end is not None:
            end = _wrap_string(end)

        self._end = end
        self._minimum_length = minimum_length

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

        if len(matched) >= self._minimum_length:
            return matched
        else:
            return None


class RepeatedDict(Repeated):
    """Matches a pattern zero or more times.

    """

    def __init__(self, element, end=None, minimum_length=0, key=None):
        super(RepeatedDict, self).__init__(element, end, minimum_length)

        if key is None:
            key = itemgetter(0)

        self._key = key

    def match(self, tokens):
        matched = {}

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

            key = self._key(mo)

            try:
                matched[key].append(mo)
            except KeyError:
                matched[key] = [mo]

        if len(matched) >= self._minimum_length:
            return matched
        else:
            return None


class ZeroOrMore(Repeated):
    """Matches a pattern zero or more times.

    """

    def __init__(self, element, end=None):
        super(ZeroOrMore, self).__init__(element, end, 0)


class ZeroOrMoreDict(RepeatedDict):
    """Matches a pattern zero or more times.

    """

    def __init__(self, element, end=None, key=None):
        super(ZeroOrMoreDict, self).__init__(element, end, 0, key)


class OneOrMore(Repeated):
    """Matches a pattern one or more times.

    """

    def __init__(self, element, end=None):
        super(OneOrMore, self).__init__(element, end, 1)


class OneOrMoreDict(RepeatedDict):
    """Matches a pattern one or more times.

    """

    def __init__(self, element, end=None, key=None):
        super(OneOrMoreDict, self).__init__(element, end, 1, key)


class Any(Pattern):
    """Matches any token.

    """

    def match(self, tokens):
        return tokens.get().value


class DelimitedList(Pattern):
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


class Optional(Pattern):
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


class Inline(Pattern):

    def __init__(self, inner):
        self._inner = inner

    def match(self, tokens):
        return self._inner.match(tokens)


class Tag(Pattern):

    def __init__(self, name, inner):
        self._name = name
        self._inner = _wrap_string(inner)

    def match(self, tokens):
        mo = self._inner.match(tokens)

        if mo is not None:
            return (self._name, mo)
        else:
            return None


class Forward(Pattern):

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

        if parsed is not None and tokens.peek().kind == '__EOF__':
            return parsed
        else:
            raise GrammarError(tokens.get().offset)


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


def line(string, offset):
    return string[:offset].count('\n') + 1


def column(string, offset):
    line_start = string.rfind('\n', 0, offset)

    return offset - line_start


def tokenize_init(spec):
    tokens = []
    re_token = '|'.join([
        '(?P<{}>{})'.format(name, regex) for name, regex in spec
    ])

    return tokens, re_token


def parse(string, tokenize, grammar):
    """Parse given string `string` using given tokenize function
    `tokenize` and grammar `grammar`.

    """

    try:
        return grammar.parse(tokenize(string))
    except (TokenizeError, GrammarError) as e:
        raise ParseError(string, e.offset)


class Parser(object):
    """A parser.

    """

    def keywords(self):
        """Keywords in the text.

        """

        return set()

    def token_specs(self):
        """The token specifications.

        """

        raise NotImplementedError('To be implemented by subclasses.')

    def _unpack_token_specs(self):
        names = {}
        specs = []

        for spec in self.token_specs():
            if len(spec) == 2:
                specs.append(spec)
            else:
                specs.append((spec[0], spec[2]))
                names[spec[0]] = spec[1]

        return names, specs

    def tokenize(self, string):
        """Tokenize the text.

        """

        names, specs = self._unpack_token_specs()
        keywords = self.keywords()
        tokens, re_token = tokenize_init(specs)

        for mo in re.finditer(re_token, string, re.DOTALL):
            kind = mo.lastgroup

            if kind == 'SKIP':
                pass
            elif kind != 'MISMATCH':
                value = mo.group(kind)

                if value in keywords:
                    kind = value

                if kind in names:
                    kind = names[kind]

                if kind == 'ESCAPED_STRING':
                    value = value[1:-1]

                tokens.append(Token(kind, value, mo.start()))
            else:
                raise TokenizeError(string, mo.start())

        return tokens

    def grammar(self):
        """The text grammar.

        """

        raise NotImplementedError('To be implemented by subclasses.')

    def parse(self, string):
        """Parse given string `string` and return the parse tree.

        """

        return parse(string, self.tokenize, self.grammar())
