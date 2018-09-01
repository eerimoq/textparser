#!/usr/bin/env python3

"""An JSON example of how to transform a parse tree of tokens into
lists, dicts, floats, booleans and None.

NOTE: The parse tree transformation is implemented as a separate step
after parsing. Making the transformation part of the parser is
probably desired, but there are currently no plans on doing so because
there is no use case at the moment (for me, probably the only user).

$ env PYTHONPATH=. python3 examples/json.py
{'number': 0.11, 'false': False, 'true': True, 'null': None, 'list': [None, 'string']}

"""

import textparser
from textparser import Forward
from textparser import Sequence
from textparser import DelimitedList
from textparser import choice
from textparser import Optional


JSON_TEXT = '''\
{
    "number": 0.11,
    "false": false,
    "true": true,
    "null": null,
    "list": [null, "string"]
}
'''


class Parser(textparser.Parser):

    def token_specs(self):
        return [
            ('SKIP',                r'[ \r\n\t]+'),
            ('NUMBER',              r'-?\d+(\.\d+)?([eE][+-]?\d+)?'),
            ('TRUE',                r'true'),
            ('FALSE',               r'false'),
            ('NULL',                r'null'),
            ('ESCAPED_STRING',      r'"(\\"|[^"])*?"'),
            ('LPAREN',         '(', r'\('),
            ('RPAREN',         ')', r'\)'),
            ('LBRACKET',       '[', r'\['),
            ('RBRACKET',       ']', r'\]'),
            ('LBRACE',         '{', r'\{'),
            ('RBRACE',         '}', r'\}'),
            ('COMMA',          ',', r','),
            ('COLON',          ':', r':'),
            ('MISMATCH',            r'.')
        ]

    def grammar(self):
        value = Forward()
        list_ = Sequence('[', Optional(DelimitedList(value)), ']')
        pair = Sequence('ESCAPED_STRING', ':', value)
        dict_ = Sequence('{', Optional(DelimitedList(pair)), '}')
        value <<= choice(list_,
                         dict_,
                         'ESCAPED_STRING',
                         'NUMBER',
                         'TRUE',
                         'FALSE',
                         'NULL')

        return value


def transform(token):
    if isinstance(token, list):
        if token[0].kind == '{':
            if len(token[1]) > 0:
                return {
                    key.value[1:-1]: transform(v)
                    for key, _, v in token[1][0]
                }
            else:
                return {}
        else:
            if len(token[1]) > 0:
                return [transform(elem) for elem in token[1][0]]
            else:
                return []
    elif token.kind == 'ESCAPED_STRING':
        return token.value[1:-1]
    elif token.kind == 'NUMBER':
        return float(token.value)
    elif token.kind == 'TRUE':
        return True
    elif token.kind == 'FALSE':
        return False
    else:
        return None


print(transform(Parser().parse(JSON_TEXT, token_tree=True)))
