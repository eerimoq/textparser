"""Based on
https://github.com/igordejanovic/textX/tree/master/examples/json.

"""

import timeit

import textx
from textx import metamodel_from_str


GRAMMAR = '''\
/*
    A grammar for JSON data-interchange format.
    See: http://www.json.org/
*/
File:
    Array | Object
;

Array:
    "[" values*=Value[','] "]"
;

Value:
    STRING | FLOAT | BOOL | Object | Array | "null"
;

Object:
    "{" members*=Member[','] "}"
;

Member:
    key=STRING ':' value=Value
;
'''


def parse_time(json_string, iterations):
    parser = metamodel_from_str(GRAMMAR)

    def _parse():
        parser.model_from_str(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    parser = metamodel_from_str(GRAMMAR)

    return parser.model_from_str(json_string)


def version():
    return textx.__version__
