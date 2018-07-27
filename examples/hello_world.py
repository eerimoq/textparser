#!/usr/bin/env python3
#
# > env PYTHONPATH=.. python3 hello_world.py
# Tree: ['Hello', ',', 'World', '!']
#

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

print('Tree:', tree)
