"""Based on
https://github.com/lark-parser/lark/blob/master/docs/json_tutorial.md.

"""

import timeit

from lark import Lark


LARK_JSON_GRAMMAR = r"""
    ?value: dict
          | list
          | string
          | SIGNED_NUMBER
          | "true"
          | "false"
          | "null"

    list : "[" [value ("," value)*] "]"

    dict : "{" [pair ("," pair)*] "}"
    pair : string ":" value

    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    """


def parse_lalr(json_string, iterations):
    parser = Lark(LARK_JSON_GRAMMAR,
                  start='value',
                  lexer='standard',
                  parser='lalr')

    def _parse():
        parser.parse(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse_earley(json_string, iterations):
    parser = Lark(LARK_JSON_GRAMMAR,
                  start='value',
                  lexer='standard',
                  parser='earley')

    def _parse():
        parser.parse(json_string)

    return timeit.timeit(_parse, number=iterations)
