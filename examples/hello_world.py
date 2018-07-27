#!/usr/bin/env python3
#
# $ env PYTHONPATH=.. python3 hello_world.py
# Tree: ['Hello', ',', 'World', '!']
#
# Token tree:
# [Token(kind='WORD', value='Hello', offset=0),
#  Token(kind=',', value=',', offset=5),
#  Token(kind='WORD', value='World', offset=7),
#  Token(kind='!', value='!', offset=12)]
#

from pprint import pprint

import textparser
from textparser import Sequence


class Parser(textparser.Parser):

    def token_specs(self):
        return [
            ('SKIP',          r'[ \r\n\t]+'),
            ('WORD',          r'\w+'),
            ('EMARK',    '!', r'!'),
            ('COMMA',    ',', r','),
            ('MISMATCH',      r'.')
        ]

    def grammar(self):
        return Sequence('WORD', ',', 'WORD', '!')


tree = Parser().parse('Hello, World!')
token_tree = Parser().parse('Hello, World!', token_tree=True)

print('Tree:', tree)
print()
print('Token tree:')
pprint(token_tree)
