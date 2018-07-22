import unittest

import textparser
from textparser import Grammar
from textparser import Sequence
from textparser import OneOrMore
from textparser import ZeroOrMore
from textparser import DelimitedList
from textparser import Token
from textparser import TokenizerError


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

    def test_zero_or_more(self):
        grammar = Grammar(ZeroOrMore('WORD'))

        datas = [
            ([], []),
            ([('WORD', 'foo')], ['foo']),
            ([('WORD', 'foo'), ('WORD', 'bar')], ['foo', 'bar'])
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_one_or_more(self):
        grammar = Grammar(OneOrMore('WORD'))

        datas = [
            ([('WORD', 'foo')], ['foo']),
            ([('WORD', 'foo'), ('WORD', 'bar')], ['foo', 'bar'])
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_one_or_more_mismatch(self):
        grammar = Grammar(OneOrMore('WORD'))

        datas = [
            [],
            [('NUMBER', 'foo')]
        ]

        for tokens in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])

            with self.assertRaises(textparser.Error) as cm:
                grammar.parse(tokens)

            self.assertEqual(str(cm.exception), '')

    def test_tokenizer_error(self):
        datas = [
            (2, 'hej', 'he>>!<<j'),
            (0, 'a\nb\n', '>>!<<a'),
            (1, 'a\nb\n', 'a>>!<<'),
            (2, 'a\nb\n', '>>!<<b')
        ]

        for offset, string, message in datas:
            with self.assertRaises(TokenizerError) as cm:
                raise TokenizerError(0, 1, offset, string)

            self.assertEqual(
                str(cm.exception),
                'Invalid syntax at line 0, column 1: "{}"'.format(message))


if __name__ == '__main__':
    unittest.main()
