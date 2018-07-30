import timeit

import parsy
from parsy import generate
from parsy import regex
from parsy import string


whitespace = regex(r'\s*')
lexeme = lambda p: p << whitespace
lbrace = lexeme(string('{'))
rbrace = lexeme(string('}'))
lbrack = lexeme(string('['))
rbrack = lexeme(string(']'))
colon  = lexeme(string(':'))
comma  = lexeme(string(','))
true   = lexeme(string('true'))
false  = lexeme(string('false'))
null   = lexeme(string('null'))
number = lexeme(
    regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
)
string_part = regex(r'[^"\\]+')
string_esc = string('\\') >> (
    string('\\')
    | string('/')
    | string('"')
    | string('b')
    | string('f')
    | string('n')
    | string('r')
    | string('t')
    | regex(r'u[0-9a-fA-F]{4}').map(lambda s: chr(int(s[1:], 16)))
)
quoted = lexeme(string('"') >> (string_part | string_esc).many().concat() << string('"'))


# Circular dependency between array and value means we use `generate`
# form here.
@generate
def array():
    yield lbrack
    elements = yield value.sep_by(comma)
    yield rbrack

    return elements


@generate
def object_pair():
    key = yield quoted
    yield colon
    val = yield value

    return (key, val)


json_object = lbrace >> object_pair.sep_by(comma) << rbrace
value = quoted | number | json_object | array | true | false | null
json = whitespace >> value


def parse_time(json_string, iterations):
    def _parse():
        json.parse(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    return json.parse(json_string)


def version():
    return parsy.__version__
