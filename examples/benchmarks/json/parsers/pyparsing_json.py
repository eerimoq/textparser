"""Based on https://github.com/pyparsing/pyparsing/blob/master/examples/jsonParser.py.

"""

import timeit

import pyparsing
from pyparsing import Keyword
from pyparsing import Suppress
from pyparsing import dblQuotedString
from pyparsing import Forward
from pyparsing import Group
from pyparsing import delimitedList
from pyparsing import Optional
from pyparsing import pyparsing_common
from pyparsing import Dict


def create_grammar():
    TRUE  = Keyword('true')
    FALSE = Keyword('false')
    NULL  = Keyword('null')

    LBRACK, RBRACK, LBRACE, RBRACE, COLON = map(Suppress, '[]{}:')

    string = dblQuotedString()
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

    return value


def parse_time(json_string, iterations=1):
    grammar = create_grammar()

    def _parse():
        grammar.parseString(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    grammar = create_grammar()
    
    return grammar.parseString(json_string).asList()


def version():
    return pyparsing.__version__
