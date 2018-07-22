#!/usr/bin/env python

"""A performance example comparing the performance of four parsers.

Lark parsers based on
https://github.com/lark-parser/lark/blob/master/docs/json_tutorial.md.

Pyparsing parser based on
http://pyparsing.wikispaces.com/file/view/jsonParser.py.

Test data generated with https://www.json-generator.com.

Example execution:

$ ./main.py
Parsing 'data.json' 3 times per parser. This may take a few seconds.

Parsing 'data.json' 3 times took:

PACKAGE        SECONDS
textparser     0.728505
lark (LALR)    1.330224
pyparsing      3.538572
lark (Earley)  9.209010
$

"""

from __future__ import print_function

import os
import re
import timeit

import textparser as tp
from lark import Lark
import pyparsing as pp


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_JSON = os.path.relpath(os.path.join(SCRIPT_DIR, 'data.json'))

ITERATIONS = 3


with open(DATA_JSON, 'r') as fin:
    JSON_STRING = fin.read()


def tokenize(string):
    names = {
        'LPAREN': '(',
        'RPAREN': ')',
        'LBRACKET': '[',
        'RBRACKET': ']',
        'LBRACE': '{',
        'RBRACE': '}',
        'COMMA':  ',',
        'COLON':  ':'
    }

    spec = [
        ('SKIP',     r'[ \r\t]+'),
        ('NUMBER',   r'-?\d+(\.\d+)?([eE][+-]?\d+)?'),
        ('TRUE',     r'true'),
        ('FALSE',    r'false'),
        ('NULL',     r'null'),
        ('NEWLINE',  r'\n'),
        ('STRING',   r'"(\\"|[^"])*?"'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('LBRACE',   r'\{'),
        ('RBRACE',   r'\}'),
        ('COMMA',    r','),
        ('COLON',    r':'),
        ('MISMATCH', r'.')
    ]

    line = 1
    line_start = -1
    tokens = []
    re_token = tp.create_token_re(spec)

    for mo in re.finditer(re_token, string, re.DOTALL):
        kind = mo.lastgroup

        if kind == 'SKIP':
            pass
        elif kind == 'NEWLINE':
            line_start = mo.end() - 1
            line += 1
        elif kind == 'STRING':
            column = mo.start() - line_start
            tokens.append(tp.Token(kind, mo.group(kind)[1:-1], line, column))
        elif kind != 'MISMATCH':
            value = mo.group(kind)

            if kind in names:
                kind = names[kind]

            column = mo.start() - line_start
            tokens.append(tp.Token(kind, value, line, column))
        else:
            column = mo.start() - line_start

            raise tp.TokenizerError(line, column, mo.start(), string)

    tokens.append(tp.Token('__EOF__', None, None, None))

    return tokens


def textparser_parse():
    value = tp.Forward()
    list_ = tp.Sequence('[', tp.DelimitedList(value), ']')
    pair = tp.Sequence('STRING', ':', value)
    dict_ = tp.Sequence('{', tp.DelimitedList(pair), '}')
    value <<= tp.choice(list_, dict_, 'STRING', 'NUMBER', 'TRUE', 'FALSE', 'NULL')
    grammar = tp.Grammar(value)

    def parse():
        grammar.parse(tokenize(JSON_STRING))

    return timeit.timeit(parse, number=ITERATIONS)


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


def lark_lalr_parse():
    parser = Lark(LARK_JSON_GRAMMAR,
                  start='value',
                  lexer='standard',
                  parser='lalr')

    def parse():
        parser.parse(JSON_STRING)

    return timeit.timeit(parse, number=ITERATIONS)


def lark_earley_parse():
    parser = Lark(LARK_JSON_GRAMMAR,
                  start='value',
                  lexer='standard',
                  parser='earley')

    def parse():
        parser.parse(JSON_STRING)

    return timeit.timeit(parse, number=ITERATIONS)


def pyparsing_parse():
    TRUE  = pp.Keyword('true')
    FALSE = pp.Keyword('false')
    NULL  = pp.Keyword('null')

    LBRACK, RBRACK, LBRACE, RBRACE, COLON = map(pp.Suppress, '[]{}:')

    string = pp.dblQuotedString().setParseAction(pp.removeQuotes)
    number = pp.pyparsing_common.number()

    object_ = pp.Forward()
    value = pp.Forward()
    elements = pp.delimitedList(value)
    array = pp.Group(LBRACK + pp.Optional(elements, []) + RBRACK)
    value <<= (string
               | number
               | pp.Group(object_)
               | array
               | TRUE
               | FALSE
               | NULL)
    member = pp.Group(string + COLON + value)
    members = pp.delimitedList(member)
    object_ <<= pp.Dict(LBRACE + pp.Optional(members) + RBRACE)

    def parse():
        value.parseString(JSON_STRING)

    return timeit.timeit(parse, number=ITERATIONS)


def main():
    print(
        "Parsing '{}' {} times per parser. This may take a few seconds.".format(
            DATA_JSON,
            ITERATIONS))

    textparser_time = textparser_parse()
    lark_lalr_time = lark_lalr_parse()
    lark_earley_time = lark_earley_parse()
    pyparsing_time = pyparsing_parse()

    # Parse comparison output.
    measurements = [
        ('textparser', textparser_time),
        ('lark (LALR)', lark_lalr_time),
        ('lark (Earley)', lark_earley_time),
        ('pyparsing', pyparsing_time)
    ]

    measurements = sorted(measurements, key=lambda m: m[1])

    print()
    print("Parsing '{}' {} times took:".format(DATA_JSON, ITERATIONS))
    print()
    print('PACKAGE        SECONDS')
    for package, seconds in measurements:
        print('{:14s} {:f}'.format(package, seconds))


if __name__ == '__main__':
    main()
