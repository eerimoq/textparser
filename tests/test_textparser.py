import unittest

import textparser
from textparser import Grammar
from textparser import Sequence
from textparser import DelimitedList
from textparser import Token


def tokenize(items):
    return [Token(*item, line=1, column=2) for item in items]


class TextParserTest(unittest.TestCase):

    def test_sequence(self):
        grammar = Grammar(Sequence('NUMBER', 'WORD'))
        tokens = tokenize([
            ('NUMBER', '1.45'),
            ('WORD', 'm'),
            ('__EOF__', '')
        ])
        tree = grammar.parse(tokens)
        self.assertEqual(tree, ['1.45', 'm'])

    def test_sequence_mismatch(self):
        grammar = Grammar(Sequence('NUMBER', 'WORD'))
        tokens = tokenize([
            ('NUMBER', '1.45'),
            ('__EOF__', '')
        ])

        with self.assertRaises(textparser.Error) as cm:
            grammar.parse(tokens)

        self.assertEqual(str(cm.exception), '')

    def test_delimited_list(self):
        grammar = Grammar(DelimitedList('WORD'))

        datas = [
            ([], []),
            ([('WORD', 'foo')], ['foo']),
            ([('WORD', 'foo'), (',', ','), ('WORD', 'bar')], ['foo', 'bar'])
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)


if __name__ == '__main__':
    unittest.main()
