import textparser
from textparser import Sequence
from textparser import Grammar


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
        return Grammar(Sequence('WORD', ',', 'WORD', '!'))


tree = Parser().parse('Hello, World!')

print('Tree:', tree)
