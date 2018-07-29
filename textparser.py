# A text parser.

import re
from collections import namedtuple
from operator import itemgetter


__author__ = 'Erik Moqvist'
__version__ = '0.13.0'


class _String(object):
    """Matches a specific token kind.

    """

    def __init__(self, kind):
        self.kind = kind

    def match(self, tokens):
        if self.kind == tokens.peek().kind:
            return tokens.get_value()
        else:
            return None


def _wrap_string(item):
    if isinstance(item, str):
        item = _String(item)

    return item


def _wrap_strings(items):
    return [_wrap_string(item) for item in items]


def _format_invalid_syntax(string, offset):
    return 'Invalid syntax at line {}, column {}: "{}"'.format(
        line(string, offset),
        column(string, offset),
        markup_line(string, offset))


class Error(Exception):
    pass


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


class Tokens(object):

    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0
        self._max_pos = -1
        self._stack = []

    def get_value(self):
        pos = self._pos
        self._pos += 1

        return self._tokens[pos]

    def peek(self):
        return self._tokens[self._pos]

    def peek_max(self):
        pos = self._pos

        if self._max_pos > pos:
            pos = self._max_pos

        return self._tokens[pos]

    def save(self):
        self._stack.append(self._pos)

    def restore(self):
        self._pos = self._stack.pop()

    def update(self):
        self._stack[-1] = self._pos

    def mark_max_restore(self):
        if self._pos > self._max_pos:
            self._max_pos = self._pos

        self._pos = self._stack.pop()

    def mark_max_load(self):
        if self._pos > self._max_pos:
            self._max_pos = self._pos

        self._pos = self._stack[-1]

    def drop(self):
        self._stack.pop()

    def __repr__(self):
        return str(self._tokens[self._pos:self._pos + 2])


class StringTokens(Tokens):

    def get_value(self):
        pos = self._pos
        self._pos += 1

        return self._tokens[pos].value


class Pattern(object):
    """Base class of all patterns.

    """
    
    def match(self, tokens):
        raise NotImplementedError('To be implemented by subclasses.')


class Sequence(Pattern):
    """Matches a sequence of patterns.

    """

    def __init__(self, *patterns):
        self.patterns = _wrap_strings(patterns)

    def match(self, tokens):
        matched = []

        for pattern in self.patterns:
            mo = pattern.match(tokens)

            if mo is None:
                return None

            matched.append(mo)

        return matched


class Choice(Pattern):
    """Matches any of given patterns.

    """

    def __init__(self, *patterns):
        self._patterns = _wrap_strings(patterns)

    def match(self, tokens):
        tokens.save()

        for pattern in self._patterns:
            tokens.mark_max_load()
            mo = pattern.match(tokens)

            if mo is not None:
                tokens.drop()

                return mo

        tokens.restore()

        return None


class ChoiceDict(Pattern):
    """Matches any of given patterns.

    The first token kind of all patterns must be unique, otherwise and
    Error exception is raised.

    """

    def __init__(self, *patterns):
        self._patterns_map = {}
        patterns = _wrap_strings(patterns)

        for pattern in patterns:
            self._check_pattern(pattern, pattern)

    @property
    def patterns_map(self):
        return self._patterns_map

    def _check_pattern(self, inner, outer):
        if isinstance(inner, _String):
            self._add_pattern(inner.kind, outer)
        elif isinstance(inner, Sequence):
            self._check_pattern(inner.patterns[0], outer)
        elif isinstance(inner, (Tag, Forward)):
            self._check_pattern(inner.pattern, outer)
        elif isinstance(inner, ChoiceDict):
            for pattern in inner.patterns_map.values():
                self._check_pattern(pattern, outer)
        else:
            raise Error(
                'Unsupported pattern type {}.'.format(type(inner)))

    def _add_pattern(self, kind, pattern):
        if kind in self._patterns_map:
            raise Error(
                "First token kind must be unique, but {} isn't.".format(
                    kind))

        self._patterns_map[kind] = pattern

    def match(self, tokens):
        kind = tokens.peek().kind

        if kind in self._patterns_map:
            return self._patterns_map[kind].match(tokens)
        else:
            return None


class Repeated(Pattern):
    """Matches given pattern `pattern` at least `minimum` times and
    returns the matches as a list.

    """

    def __init__(self, pattern, end=None, minimum=0):
        self._pattern = _wrap_string(pattern)

        if end is not None:
            end = _wrap_string(end)

        self._end = end
        self._minimum = minimum

    def match(self, tokens):
        matched = []
        tokens.save()

        while True:
            if self._end is not None:
                tokens.save()
                mo = self._end.match(tokens)
                tokens.restore()

                if mo is not None:
                    tokens.drop()
                    break

            mo = self._pattern.match(tokens)

            if mo is None:
                tokens.mark_max_restore()
                break

            matched.append(mo)
            tokens.update()

        if len(matched) >= self._minimum:
            return matched
        else:
            return None


class RepeatedDict(Repeated):
    """Matches given pattern `pattern` at lead `minimum` times and returns
    the matches as a dictionary.

    """

    def __init__(self, pattern, end=None, minimum=0, key=None):
        super(RepeatedDict, self).__init__(pattern, end, minimum)

        if key is None:
            key = itemgetter(0)

        self._key = key

    def match(self, tokens):
        matched = {}
        tokens.save()

        while True:
            if self._end is not None:
                tokens.save()
                mo = self._end.match(tokens)
                tokens.restore()

                if mo is not None:
                    tokens.drop()
                    break

            mo = self._pattern.match(tokens)

            if mo is None:
                tokens.mark_max_restore()
                break

            key = self._key(mo)

            try:
                matched[key].append(mo)
            except KeyError:
                matched[key] = [mo]

            tokens.update()

        if len(matched) >= self._minimum:
            return matched
        else:
            return None


class ZeroOrMore(Repeated):
    """Matches `pattern` zero or more times and returns the matches as a
    list.

    """

    def __init__(self, pattern, end=None):
        super(ZeroOrMore, self).__init__(pattern, end, 0)


class ZeroOrMoreDict(RepeatedDict):
    """Matches `pattern` zero or more times and returns the matches as a
    dictionary.

    """

    def __init__(self, pattern, end=None, key=None):
        super(ZeroOrMoreDict, self).__init__(pattern, end, 0, key)


class OneOrMore(Repeated):
    """Matches `pattern` one or more times and returns the matches as a
    list.

    """

    def __init__(self, pattern, end=None):
        super(OneOrMore, self).__init__(pattern, end, 1)


class OneOrMoreDict(RepeatedDict):
    """Matches `pattern` one or more times and returns the matches as a
    dictionary.

    """

    def __init__(self, pattern, end=None, key=None):
        super(OneOrMoreDict, self).__init__(pattern, end, 1, key)


class DelimitedList(Pattern):
    """Matches a delimented list of `pattern` separated by `delim`.

    """

    def __init__(self, pattern, delim=','):
        self._pattern = _wrap_string(pattern)
        self._delim = _wrap_string(delim)

    def match(self, tokens):
        # First pattern.
        mo = self._pattern.match(tokens)

        if mo is None:
            return None

        matched = [mo]
        tokens.save()

        while True:
            # Discard the delimiter.
            mo = self._delim.match(tokens)

            if mo is None:
                break

            # Pattern.
            mo = self._pattern.match(tokens)

            if mo is None:
                break

            matched.append(mo)
            tokens.update()

        tokens.restore()

        return matched


class Optional(Pattern):
    """Matches `pattern` zero or one times.

    """

    def __init__(self, pattern):
        self._pattern = _wrap_string(pattern)

    def match(self, tokens):
        tokens.save()
        mo = self._pattern.match(tokens)

        if mo is None:
            tokens.mark_max_restore()

            return []
        else:
            tokens.drop()

            return [mo]


class Any(Pattern):
    """Matches any token.

    """

    def match(self, tokens):
        return tokens.get_value()


class Not(Pattern):
    """Does not match given pattern.

    """

    def __init__(self, pattern):
        self._pattern = _wrap_string(pattern)

    def match(self, tokens):
        tokens.save()
        mo = self._pattern.match(tokens)
        tokens.restore()

        if mo is None:
            return []
        else:
            return None


class NoMatch(Pattern):
    """Never matches anything.

    """

    def match(self, tokens):
        return None


class Tag(Pattern):
    """Tags any matched `pattern` with `name`.

    """

    def __init__(self, name, pattern):
        self._name = name
        self._pattern = _wrap_string(pattern)

    @property
    def pattern(self):
        return self._pattern

    def match(self, tokens):
        mo = self._pattern.match(tokens)

        if mo is not None:
            return (self._name, mo)
        else:
            return None


class Forward(Pattern):
    """Forward declaration of a pattern.

    .. code-block:: python

       >>> foo = Forward()
       >>> foo <<= Sequence('NUMBER')

    """

    def __init__(self):
        self._pattern = None

    @property
    def pattern(self):
        return self._pattern

    def __ilshift__(self, other):
        self._pattern = _wrap_string(other)

        return self

    def match(self, tokens):
        return self._pattern.match(tokens)


class Grammar(object):
    """Creates a tree of given tokens.

    """

    def __init__(self, grammar):
        self._root = grammar

    def parse(self, tokens, token_tree=False):
        if token_tree:
            tokens = Tokens(tokens)
        else:
            tokens = StringTokens(tokens)

        parsed = self._root.match(tokens)

        if parsed is not None and tokens.peek_max().kind == '__EOF__':
            return parsed
        else:
            raise GrammarError(tokens.peek_max().offset)


def choice(*patterns):
    try:
        return ChoiceDict(*patterns)
    except Error:
        return Choice(*patterns)


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


class Parser(object):
    """The abstract base class of all text parsers.

    .. code-block:: python

       >>> from textparser import Parser, Sequence
       >>> class MyParser(Parser):
       ...    def token_specs(self):
       ...        return [
       ...            ('SKIP',          r'[ \\r\\n\\t]+'),
       ...            ('WORD',          r'\\w+'),
       ...            ('EMARK',    '!', r'!'),
       ...            ('COMMA',    ',', r','),
       ...            ('MISMATCH',      r'.')
       ...        ]
       ...    def grammar(self):
       ...        return Sequence('WORD', ',', 'WORD', '!')

    """

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

    def keywords(self):
        """Keywords in the text.

        """

        return set()

    def token_specs(self):
        """The token specifications with token name, regular expression, and
        optionally a user friendly name.

        Two token specification forms are available; ``(kind, re)`` or
        ``(kind, name, re)``. If the second form is used, the grammar
        should use `name` instead of `kind`.


        """

        return []

    def tokenize(self, string):
        """Tokenize given text `string`, and return a list of tokens.

        This method should only be called by
        :func:`~textparser.Parser.parse()`, but may very well be
        overridden if the default implementation does not match the
        parser needs.

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

                tokens.append(Token(kind, value, mo.start()))
            else:
                raise TokenizeError(string, mo.start())

        return tokens

    def grammar(self):
        """The text grammar is used to create a parse tree out of a list of
        tokens.


        """

        raise NotImplementedError('To be implemented by subclasses.')

    def parse(self, string, token_tree=False):
        """Parse given string `string` and return the parse tree.

        Returns a parse tree of tokens if `token_tree` is ``True``.

        .. code-block:: python

           >>> MyParser().parse('Hello, World!')
           ['Hello', ',', 'World', '!']
           >>> tree = MyParser().parse('Hello, World!', token_tree=True)
           >>> from pprint import pprint
           >>> pprint(tree)
           [Token(kind='WORD', value='Hello', offset=0),
            Token(kind=',', value=',', offset=5),
            Token(kind='WORD', value='World', offset=7),
            Token(kind='!', value='!', offset=12)]

        """

        try:
            tokens = self.tokenize(string)

            if len(tokens) == 0 or tokens[-1].kind != '__EOF__':
                tokens.append(Token('__EOF__', None, len(string)))

            return Grammar(self.grammar()).parse(tokens, token_tree)
        except (TokenizeError, GrammarError) as e:
            raise ParseError(string, e.offset)
