import unittest

import textparser
from textparser import Grammar
from textparser import Sequence
from textparser import Choice
from textparser import ChoiceDict
from textparser import OneOrMore
from textparser import ZeroOrMore
from textparser import DelimitedList
from textparser import Token
from textparser import TokenizerError
from textparser import create_token_re
from textparser import Any


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
        tokens = tokenize([('NUMBER', '1.45'), ('__EOF__', '')])

        with self.assertRaises(textparser.Error) as cm:
            grammar.parse(tokens)

        self.assertEqual(str(cm.exception), '')

    def test_choice(self):
        grammar = Grammar(Choice('NUMBER', 'WORD'))

        datas = [
            ([('WORD', 'm')], 'm'),
            ([('NUMBER', '5')], '5')
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_choice_mismatch(self):
        grammar = Grammar(Choice('NUMBER', 'WORD'))
        tokens = tokenize([(',', ','), ('__EOF__', '')])

        with self.assertRaises(textparser.Error) as cm:
            grammar.parse(tokens)

        self.assertEqual(str(cm.exception), '')

    def test_choice_dict(self):
        grammar = Grammar(ChoiceDict(Sequence('NUMBER'),
                                     Sequence('WORD')))

        datas = [
            ([('WORD', 'm')], ['m']),
            ([('NUMBER', '5')], ['5'])
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_choice_dict_mismatch(self):
        grammar = Grammar(ChoiceDict(Sequence('NUMBER'),
                                     Sequence('WORD')))
        tokens = tokenize([(',', ','), ('__EOF__', '')])

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

    def test_delimited_list_mismatch(self):
        grammar = Grammar(DelimitedList('WORD'))

        datas = [
            [('WORD', 'foo'), (',', ',')]
        ]

        for tokens in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])

            with self.assertRaises(textparser.Error) as cm:
                grammar.parse(tokens)

            self.assertEqual(str(cm.exception), '')

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

    def test_zero_or_more_end(self):
        grammar = Grammar(
            Sequence(ZeroOrMore('WORD', Sequence('WORD', 'NUMBER')),
                     Sequence('WORD', 'NUMBER')))

        datas = [
            (
                [('WORD', 'bar'), ('NUMBER', '1')],
                [[], ['bar', '1']]
            ),
            (
                [('WORD', 'foo'), ('WORD', 'bar'), ('NUMBER', '1')],
                [['foo'], ['bar', '1']]
            )
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

    def test_one_or_more_end(self):
        grammar = Grammar(
            Sequence(OneOrMore('WORD', Sequence('WORD', 'NUMBER')),
                     Sequence('WORD', 'NUMBER')))

        datas = [
            (
                [('WORD', 'foo'), ('WORD', 'bar'), ('NUMBER', '1')],
                [['foo'], ['bar', '1']]
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_one_or_more_end_mismatch(self):
        grammar = Grammar(OneOrMore('WORD', Sequence('WORD', 'NUMBER')))

        datas = [
            [('WORD', 'bar'), ('NUMBER', '1')]
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

    def test_create_token_re(self):
        datas = [
            ([('A', r'a')], '(?P<A>a)'),
            ([('A', r'b'), ('C', r'd')], '(?P<A>b)|(?P<C>d)')
        ]

        for spec, re_token in datas:
            self.assertEqual(create_token_re(spec), re_token)

    def test_any(self):
        grammar = Grammar(Any())

        datas = [
            ([('A', r'a')], 'a'),
            ([('B', r'b')], 'b')
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)


if __name__ == '__main__':
    unittest.main()
