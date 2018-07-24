import re
import timeit

from textparser import tokenize_init
from textparser import Token
from textparser import TokenizeError
from textparser import Forward
from textparser import Sequence
from textparser import DelimitedList
from textparser import choice
from textparser import Grammar


def tokenize(string):
    names = {
        'LPAREN':   '(',
        'RPAREN':   ')',
        'LBRACKET': '[',
        'RBRACKET': ']',
        'LBRACE':   '{',
        'RBRACE':   '}',
        'COMMA':    ',',
        'COLON':    ':'
    }

    spec = [
        ('SKIP',     r'[ \r\n\t]+'),
        ('NUMBER',   r'-?\d+(\.\d+)?([eE][+-]?\d+)?'),
        ('TRUE',     r'true'),
        ('FALSE',    r'false'),
        ('NULL',     r'null'),
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

    tokens, re_token = tokenize_init(spec)

    for mo in re.finditer(re_token, string, re.DOTALL):
        kind = mo.lastgroup

        if kind == 'SKIP':
            pass
        elif kind == 'STRING':
            tokens.append(Token(kind, mo.group(kind)[1:-1], mo.start()))
        elif kind != 'MISMATCH':
            value = mo.group(kind)

            if kind in names:
                kind = names[kind]

            tokens.append(Token(kind, value, mo.start()))
        else:
            raise TokenizeError(string, mo.start())

    return tokens


def parse(json_string, iterations):
    value = Forward()
    list_ = Sequence('[', DelimitedList(value), ']')
    pair = Sequence('STRING', ':', value)
    dict_ = Sequence('{', DelimitedList(pair), '}')
    value <<= choice(list_, dict_, 'STRING', 'NUMBER', 'TRUE', 'FALSE', 'NULL')
    grammar = Grammar(value)

    def _parse():
        grammar.parse(tokenize(json_string))

    return timeit.timeit(_parse, number=iterations)
