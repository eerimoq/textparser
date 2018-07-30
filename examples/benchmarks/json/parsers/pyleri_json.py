"""Based on
https://github.com/transceptor-technology/pyleri/blob/master/examples/json_grammar.py.

"""

import timeit

import pyleri
from pyleri import Ref
from pyleri import Choice
from pyleri import Grammar
from pyleri import Regex
from pyleri import Keyword
from pyleri import Sequence
from pyleri import List


class JsonGrammar(Grammar):
    START = Ref()

    # JSON strings should be enclosed in double quotes.
    # A backslash can be used as escape character.
    r_string = Regex('(")(?:(?=(\\\?))\\2.)*?\\1')

    # JSON does not support floats or integers prefixed with a + sign
    # and floats must start with a number, for example .5 is not allowed
    # but should be written like 0.5
    r_float = Regex('-?[0-9]+\.?[0-9]+')
    r_integer = Regex('-?[0-9]+')

    k_true = Keyword('true')
    k_false = Keyword('false')
    k_null = Keyword('null')

    json_map_item = Sequence(r_string, ':', START)

    json_map = Sequence('{', List(json_map_item), '}')
    json_array = Sequence('[', List(START), ']')

    START = Choice(r_string,
                   r_float,
                   r_integer,
                   k_true,
                   k_false,
                   k_null,
                   json_map,
                   json_array)

    
def parse_time(json_string, iterations):
    grammar = JsonGrammar()

    def _parse():
        grammar.parse(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    return JsonGrammar().parse(json_string)


def version():
    return pyleri.__version__
