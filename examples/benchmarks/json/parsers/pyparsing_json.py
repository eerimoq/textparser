"""Based on http://pyparsing.wikispaces.com/file/view/jsonParser.py.

"""

import timeit

from pyparsing import Keyword
from pyparsing import Suppress
from pyparsing import dblQuotedString
from pyparsing import removeQuotes
from pyparsing import Forward
from pyparsing import Group
from pyparsing import delimitedList
from pyparsing import Optional
from pyparsing import pyparsing_common
from pyparsing import Dict


def parse(json_string, iterations):
    TRUE  = Keyword('true')
    FALSE = Keyword('false')
    NULL  = Keyword('null')

    LBRACK, RBRACK, LBRACE, RBRACE, COLON = map(Suppress, '[]{}:')

    string = dblQuotedString().setParseAction(removeQuotes)
    number = pyparsing_common.number()

    object_ = Forward()
    value = Forward()
    elements = delimitedList(value)
    array = Group(LBRACK + Optional(elements, []) + RBRACK)
    value <<= (string
               | number
               | Group(object_)
               | array
               | TRUE
               | FALSE
               | NULL)
    member = Group(string + COLON + value)
    members = delimitedList(member)
    object_ <<= Dict(LBRACE + Optional(members) + RBRACE)

    def _parse():
        value.parseString(json_string)

    return timeit.timeit(_parse, number=iterations)
