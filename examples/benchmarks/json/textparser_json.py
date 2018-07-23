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

    line, line_start, tokens, re_token = tokenize_init(spec)

    for mo in re.finditer(re_token, string, re.DOTALL):
        kind = mo.lastgroup

        if kind == 'SKIP':
            pass
        elif kind == 'NEWLINE':
            line_start = mo.end() - 1
            line += 1
        elif kind == 'STRING':
            column = mo.start() - line_start
            tokens.append(Token(kind, mo.group(kind)[1:-1], line, column))
        elif kind != 'MISMATCH':
            value = mo.group(kind)

            if kind in names:
                kind = names[kind]

            column = mo.start() - line_start
            tokens.append(Token(kind, value, line, column))
        else:
            column = mo.start() - line_start

            raise TokenizeError(line, column, mo.start(), string)

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
