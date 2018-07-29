#!/usr/bin/env python

"""Parse error comparsion for a few JSON parsers.

Example execution:

$ env PYTHONPATH=. python3 examples/benchmarks/json/errors.py
-----------------------------------------------------------------

Input string between BEGIN and END:

BEGIN
END

textparser: "Invalid syntax at line 1, column 1: ">>!<<""

lark_lalr: "'NoneType' object has no attribute 'pos_in_stream'"

lark_earley: "Incomplete parse: Could not find a solution to input"

pyparsing: "Expected {string enclosed in double quotes | real number with scientific notation | real number | signed integer | Group:(Forward: ...) | Group:({Suppress:("[") [Forward: ... [, Forward: ...]...] Suppress:("]")}) | "true" | "false" | "null"} (at char 0), (line:1, col:1)"

parsita: "No exception raised!"

funcparserlib: "no tokens left in the stream: <EOF>"

parsy: "expected one of '"', '-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?', '[', 'false', 'null', 'true', '{' at 0:0"

parsimonious: "Rule 'json_file' didn't match at '' (line 1, column 1)."

-----------------------------------------------------------------

Input string between BEGIN and END:

BEGIN
[
  1,
  {"a": {]}
]
END

textparser: "Invalid syntax at line 3, column 10: "  {"a": {>>!<<]}""

lark_lalr: "Unexpected token Token(RSQB, ']') at line 3, column 10.
Expected: string, RBRACE, ESCAPED_STRING, pair
"

lark_earley: "Unexpected token Token(RSQB, ']') at line 3, column 10.
Expected: ESCAPED_STRING, RBRACE
"

pyparsing: "Expected {string enclosed in double quotes | real number with scientific notation | real number | signed integer | Group:(Forward: ...) | Group:({Suppress:("[") [Forward: ... [, Forward: ...]...] Suppress:("]")}) | "true" | "false" | "null"} (at char 5), (line:2, col:4)"

parsita: "No exception raised!"

funcparserlib: "got unexpected token: 3,10-3,10: Op ']'"

parsy: "expected one of '"', '}' at 2:9"

parsimonious: "Rule 'members' didn't match at ']}
]
' (line 3, column 10)."

-----------------------------------------------------------------

Input string between BEGIN and END:

BEGIN
[
  1,
  {3: null}
]
END

textparser: "Invalid syntax at line 3, column 4: "  {>>!<<3: null}""

lark_lalr: "Unexpected token Token(SIGNED_NUMBER, '3') at line 3, column 4.
Expected: RBRACE, pair, ESCAPED_STRING, string
"

lark_earley: "Unexpected token Token(SIGNED_NUMBER, '3') at line 3, column 4.
Expected: ESCAPED_STRING, RBRACE
"

pyparsing: "Expected {string enclosed in double quotes | real number with scientific notation | real number | signed integer | Group:(Forward: ...) | Group:({Suppress:("[") [Forward: ... [, Forward: ...]...] Suppress:("]")}) | "true" | "false" | "null"} (at char 5), (line:2, col:4)"

parsita: "No exception raised!"

funcparserlib: "got unexpected token: 3,4-3,4: Number '3'"

parsy: "expected one of '"', '}' at 2:3"

parsimonious: "Rule 'members' didn't match at '3: null}
]
' (line 3, column 4)."

-----------------------------------------------------------------

Input string between BEGIN and END:

BEGIN
nul
END

textparser: "Invalid syntax at line 1, column 1: ">>!<<nul""

lark_lalr: "No terminal defined for 'n' at line 1 col 1

nul
^
"

lark_earley: "No terminal defined for 'n' at line 1 col 1

nul
^
"

pyparsing: "Expected {string enclosed in double quotes | real number with scientific notation | real number | signed integer | Group:(Forward: ...) | Group:({Suppress:("[") [Forward: ... [, Forward: ...]...] Suppress:("]")}) | "true" | "false" | "null"} (at char 0), (line:1, col:1)"

parsita: "No exception raised!"

funcparserlib: "got unexpected token: 1,1-1,3: Name 'nul'"

parsy: "expected one of '"', '-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?', '[', 'false', 'null', 'true', '{' at 0:0"

parsimonious: "Rule 'json_file' didn't match at 'nul
' (line 1, column 1)."
$

"""

from __future__ import print_function

from parsers import textparser_json
from parsers import lark_json
from parsers import pyparsing_json
from parsers import funcparserlib_json
from parsers import parsimonious_json

try:
    from parsers import parsita_json
except:

    class parsita_json(object):

        @staticmethod
        def parse(_json_string):
            raise Exception('Import failed!')

try:
    from parsers import parsy_json
except:
    class parsy_json(object):

        @staticmethod
        def parse(_json_string):
            raise Exception('Import failed!')


def parse(string):
    def _parse(function):
        try:
            function(string)
        except Exception as e:
            return str(e)

        return 'No exception raised!'

    results = [
        ('textparser', _parse(textparser_json.parse)),
        ('lark_lalr', _parse(lark_json.parse_lalr)),
        ('lark_earley', _parse(lark_json.parse_earley)),
        ('pyparsing', _parse(pyparsing_json.parse)),
        ('parsita', _parse(parsita_json.parse)),
        ('funcparserlib', _parse(funcparserlib_json.parse)),
        ('parsy', _parse(parsy_json.parse)),
        ('parsimonious', _parse(parsimonious_json.parse))
    ]

    print('-----------------------------------------------------------------')
    print()
    print('Input string between BEGIN and END:')
    print()
    print('BEGIN')
    print(string, end='')
    print('END')
    print()

    for parser, error in results:
        print('{}: "{}"'.format(parser, error))
        print()


EMPTY_STRING = '''\
'''

BAD_DICT_END_STRING = '''\
[
  1,
  {"a": {]}
]
'''

BAD_DICT_KEY_STRING = '''\
[
  1,
  {3: null}
]
'''

BAD_NULL_STRING = '''\
nul
'''


parse(EMPTY_STRING)
parse(BAD_DICT_END_STRING)
parse(BAD_DICT_KEY_STRING)
parse(BAD_NULL_STRING)
