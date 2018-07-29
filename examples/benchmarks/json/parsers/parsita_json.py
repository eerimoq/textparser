"""Based on
https://github.com/drhagen/parsita/blob/master/examples/json.py.

"""

import timeit

from parsita import TextParsers
from parsita import lit
from parsita import reg
from parsita import rep
from parsita import repsep


class JsonStringParsers(TextParsers, whitespace=None):
    quote = lit(r'\"')
    reverse_solidus = lit(r'\\')
    solidus = lit(r'\/')
    backspace = lit(r'\b')
    form_feed = lit(r'\f')
    line_feed = lit(r'\n')
    carriage_return = lit(r'\r')
    tab = lit(r'\t')
    uni = reg(r'\\u([0-9a-fA-F]{4})')

    escaped = (quote | reverse_solidus | solidus | backspace | form_feed |
               line_feed | carriage_return | tab | uni)
    unescaped = reg(r'[\u0020-\u0021\u0023-\u005B\u005D-\U0010FFFF]+')

    string = '"' >> rep(escaped | unescaped) << '"' > ''.join


class JsonParsers(TextParsers, whitespace=r'[ \t\n\r]*'):
    number = reg(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][-+]?[0-9]+)?')

    false = lit('false')
    true = lit('true')
    null = lit('null')

    string = JsonStringParsers.string

    array = '[' >> repsep(value, ',') << ']'

    entry = string << ':' & value
    obj = '{' >> repsep(entry, ',') << '}'

    value = (number
             | false
             | true
             | null
             | string
             | array
             | obj)


def parse_time(json_string, iterations):
    def _parse():
        JsonParsers.value.parse(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    return JsonParsers.value.parse(json_string)
