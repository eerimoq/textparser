import unittest

import textparser
from textparser import Grammar
from textparser import Sequence
from textparser import Choice
from textparser import choice
from textparser import ChoiceDict
from textparser import ZeroOrMore
from textparser import ZeroOrMoreDict
from textparser import OneOrMore
from textparser import OneOrMoreDict
from textparser import DelimitedList
from textparser import Token
from textparser import TokenizeError
from textparser import tokenize_init
from textparser import Any
from textparser import Optional
from textparser import Inline
from textparser import Tag
from textparser import Forward


def tokenize(items):
    tokens = []

    for item in items:
        if len(item) == 2:
            token = Token(*item, offset=1)
        else:
            token = Token(*item)

        tokens.append(token)

    return tokens


class TextParserTest(unittest.TestCase):

    def test_parse(self):
        def _tokenize(_string):
            return tokenize([
                ('NUMBER', '1.45'),
                ('WORD', 'm')
            ])

        grammar = Grammar(Sequence('NUMBER', 'WORD'))
        tree = textparser.parse('', _tokenize, grammar)
        self.assertEqual(tree, ['1.45', 'm'])

    def test_parse_tokenize_mismatch(self):
        def _tokenize(string):
            raise TokenizeError(string, 5)

        grammar = Grammar(Sequence('NUMBER', 'WORD'))

        with self.assertRaises(textparser.ParseError) as cm:
            textparser.parse('12\n3456\n789', _tokenize, grammar)

        self.assertEqual(cm.exception.offset, 5)
        self.assertEqual(cm.exception.line, 2)
        self.assertEqual(cm.exception.column, 3)
        self.assertEqual(str(cm.exception),
                         'Invalid syntax at line 2, column 3: "34>>!<<56"')

    def test_parse_grammar_mismatch(self):
        def _tokenize(_string):
            return tokenize([
                ('NUMBER', '1.45', 0),
                ('NUMBER', '2', 5)
            ])

        grammar = Grammar(Sequence('NUMBER', 'WORD'))

        with self.assertRaises(textparser.ParseError) as cm:
            textparser.parse('1.45 2', _tokenize, grammar)

        self.assertEqual(cm.exception.offset, 5)
        self.assertEqual(cm.exception.line, 1)
        self.assertEqual(cm.exception.column, 6)
        self.assertEqual(str(cm.exception),
                         'Invalid syntax at line 1, column 6: "1.45 >>!<<2"')

    def test_grammar_sequence(self):
        grammar = Grammar(Sequence('NUMBER', 'WORD'))
        tokens = tokenize([
            ('NUMBER', '1.45'),
            ('WORD', 'm')
        ])
        tree = grammar.parse(tokens)
        self.assertEqual(tree, ['1.45', 'm'])

    def test_grammar_sequence_mismatch(self):
        grammar = Grammar(Sequence('NUMBER', 'WORD'))
        tokens = tokenize([('NUMBER', '1.45')])

        with self.assertRaises(textparser.GrammarError) as cm:
            grammar.parse(tokens)

        self.assertEqual(cm.exception.offset, -1)

    def test_grammar_choice(self):
        grammar = Grammar(Choice('NUMBER', 'WORD'))

        datas = [
            (
                [('WORD', 'm')],
                'm'
            ),
            (
                [('NUMBER', '5')],
                '5'
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_choice_mismatch(self):
        grammar = Grammar(Choice('NUMBER', 'WORD'))
        tokens = tokenize([(',', ',', 5)])

        with self.assertRaises(textparser.GrammarError) as cm:
            grammar.parse(tokens)

        self.assertEqual(cm.exception.offset, 5)

    def test_grammar_choice_dict(self):
        grammar = Grammar(ChoiceDict(Sequence('NUMBER'), 'WORD'))

        datas = [
            (
                [('WORD', 'm')],
                'm'
            ),
            (
                [('NUMBER', '5')],
                ['5']
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_choice_dict_mismatch(self):
        grammar = Grammar(ChoiceDict(Sequence('NUMBER'),
                                     Sequence('WORD')))
        tokens = tokenize([(',', ',', 3)])

        with self.assertRaises(textparser.Error) as cm:
            grammar.parse(tokens)

        self.assertEqual(cm.exception.offset, 3)

    def test_grammar_delimited_list(self):
        grammar = Grammar(DelimitedList('WORD'))

        datas = [
            (
                [('WORD', 'foo')],
                ['foo']
            ),
            (
                [('WORD', 'foo'), (',', ','), ('WORD', 'bar')],
                ['foo', 'bar']
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_delimited_list_mismatch(self):
        grammar = Grammar(DelimitedList('WORD'))

        datas = [
            [('WORD', 'foo'), (',', ',')]
        ]

        for tokens in datas:
            tokens = tokenize(tokens)

            with self.assertRaises(textparser.GrammarError) as cm:
                grammar.parse(tokens)

            self.assertEqual(cm.exception.offset, -1)

    def test_grammar_zero_or_more(self):
        grammar = Grammar(ZeroOrMore('WORD'))

        datas = [
            (
                [],
                []
            ),
            (
                [('WORD', 'foo')],
                ['foo']
            ),
            (
                [('WORD', 'foo'), ('WORD', 'bar')],
                ['foo', 'bar']
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_zero_or_more_end(self):
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
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_zero_or_more_dict(self):
        grammar = Grammar(ZeroOrMoreDict(Sequence('WORD', 'NUMBER')))

        datas = [
            (
                [],
                {}
            ),
            (
                [('WORD', 'foo'), ('NUMBER', '1'),
                 ('WORD', 'bar'), ('NUMBER', '2'),
                 ('WORD', 'foo'), ('NUMBER', '3')],
                {
                    'foo': [['foo', '1'], ['foo', '3']],
                    'bar': [['bar', '2']]
                }
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_one_or_more(self):
        grammar = Grammar(OneOrMore('WORD'))

        datas = [
            (
                [('WORD', 'foo')],
                ['foo']
            ),
            (
                [('WORD', 'foo'), ('WORD', 'bar')],
                ['foo', 'bar']
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_one_or_more_mismatch(self):
        grammar = Grammar(OneOrMore('WORD'))

        datas = [
            (
                []
                , -1
            ),
            (
                [('NUMBER', 'foo', 2)],
                2
            )
        ]

        for tokens, offset in datas:
            tokens = tokenize(tokens)

            with self.assertRaises(textparser.GrammarError) as cm:
                grammar.parse(tokens)

            self.assertEqual(cm.exception.offset, offset)

    def test_grammar_one_or_more_end(self):
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
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_one_or_more_end_mismatch(self):
        grammar = Grammar(OneOrMore('WORD', Sequence('WORD', 'NUMBER')))

        datas = [
            [('WORD', 'bar', 1), ('NUMBER', '1', 2)]
        ]

        for tokens in datas:
            tokens = tokenize(tokens)

            with self.assertRaises(textparser.GrammarError) as cm:
                grammar.parse(tokens)

            self.assertEqual(cm.exception.offset, 1)

    def test_grammar_one_or_more_dict(self):
        grammar = Grammar(OneOrMoreDict(Sequence('WORD', 'NUMBER')))

        datas = [
            (
                [('WORD', 'foo'), ('NUMBER', '1')],
                {
                    'foo': [['foo', '1']]
                }
            ),
            (
                [('WORD', 'foo'), ('NUMBER', '1'),
                 ('WORD', 'bar'), ('NUMBER', '2'),
                 ('WORD', 'foo'), ('NUMBER', '3')],
                {
                    'foo': [['foo', '1'], ['foo', '3']],
                    'bar': [['bar', '2']]
                }
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens + [('__EOF__', '')])
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_one_or_more_dict_mismatch(self):
        grammar = Grammar(OneOrMoreDict(Sequence('WORD', 'NUMBER')))

        datas = [
            [('WORD', 'foo')]
        ]

        for tokens in datas:
            tokens = tokenize(tokens)

            with self.assertRaises(textparser.GrammarError) as cm:
                grammar.parse(tokens)

            self.assertEqual(cm.exception.offset, -1)

    def test_grammar_any(self):
        grammar = Grammar(Any())

        datas = [
            (
                [('A', r'a')],
                'a'
            ),
            (
                [('B', r'b')],
                'b'
            )
        ]

        for tokens, expected_tree in datas:
            tokens = tokenize(tokens)
            tree = grammar.parse(tokens)
            self.assertEqual(tree, expected_tree)

    def test_grammar_1(self):
        grammar = Grammar(Sequence(
            'IF',
            Inline(choice(Sequence(choice('A', 'B'), 'STRING'),
                          'STRING')),
            'WORD',
            choice(
                Sequence(
                    choice(DelimitedList('STRING'), ZeroOrMore('NUMBER')), '.'),
            '.')))

        datas = [
            (
                [
                    ('IF', 'IF'),
                    ('STRING', 'foo'),
                    ('WORD', 'bar'),
                    ('.', '.')
                ],
                ['IF', 'foo', 'bar', [[], '.']]
            ),
            (
                [
                    ('IF', 'IF'),
                    ('STRING', 'foo'),
                    ('WORD', 'bar'),
                    ('NUMBER', '0'),
                    ('NUMBER', '100'),
                    ('.', '.')
                ],
                ['IF', 'foo', 'bar', [['0', '100'], '.']]
            )
        ]

        for tokens, expected_tree in datas:
            tree = grammar.parse(tokenize(tokens))
            self.assertEqual(tree, expected_tree)

    def test_grammar_1_mismatch(self):
        grammar = Grammar(Sequence(
            'IF',
            Inline(choice(Sequence(choice('A', 'B'), 'STRING'),
                          'STRING')),
            'WORD',
            choice(
                Sequence(
                    choice(DelimitedList('STRING'), ZeroOrMore('NUMBER')), '.'),
            '.')))

        datas = [
            (
                [
                    ('IF', 'IF', 1),
                    ('STRING', 'foo', 2),
                    ('WORD', 'bar', 3),
                    (',', ',', 4)
                ],
                4
            ),
            (
                [
                    ('IF', 'IF', 1),
                    ('STRING', 'foo', 2),
                    ('.', '.', 3)
                ],
                3
            ),
            (
                [
                    ('IF', 'IF', 1),
                    ('NUMBER', '1', 2)
                ],
                2
            ),
            (
                [
                    ('IF', 'IF', 1),
                    ('STRING', 'foo', 2),
                    ('WORD', 'bar', 3),
                    ('.', '.', 4),
                    ('.', '.', 5)
                ],
                5
            )
        ]

        for tokens, offset in datas:
            tokens = tokenize(tokens)

            with self.assertRaises(textparser.GrammarError) as cm:
                grammar.parse(tokens)

            self.assertEqual(cm.exception.offset, offset)

    def test_grammar_forward(self):
        foo = Forward()
        foo <<= Sequence('FOO')
        grammar = Grammar(foo)

        datas = [
            (
                [('FOO', 'foo')],
                ['foo']
            )
        ]

        for tokens, expected_tree in datas:
            tree = grammar.parse(tokenize(tokens))
            self.assertEqual(tree, expected_tree)

    def test_grammar_optional(self):
        grammar = Grammar(Sequence(Optional('WORD'),
                                   Optional('WORD'),
                                   Optional('NUMBER')))

        datas = [
            (
                [],
                [[], [], []]
            ),
            (
                [('WORD', 'a')],
                [['a'], [], []]
            ),
            (
                [('NUMBER', 'c')],
                [[], [], ['c']]
            ),
            (
                [('WORD', 'a'), ('NUMBER', 'c')],
                [['a'], [], ['c']]
            ),
            (
                [('WORD', 'a'), ('WORD', 'b'), ('NUMBER', 'c')],
                [['a'], ['b'], ['c']]
            )
        ]

        for tokens, expected_tree in datas:
            tree = grammar.parse(tokenize(tokens))
            self.assertEqual(tree, expected_tree)

    def test_grammar_tag(self):
        grammar = Grammar(Tag('a',
                              Tag('b',
                                  choice(Tag('c', 'WORD'),
                                         Tag('d', Optional('NUMBER'))))))

        datas = [
            (
                [('WORD', 'bar')],
                ('a', ('b', ('c', 'bar')))
            ),
            (
                [('NUMBER', '1')],
                ('a', ('b', ('d', ['1'])))
            ),
            (
                [],
                ('a', ('b', ('d', [])))
            )
        ]

        for tokens, expected_tree in datas:
            tree = grammar.parse(tokenize(tokens))
            self.assertEqual(tree, expected_tree)

    def test_grammar_tag_mismatch(self):
        grammar = Grammar(Tag('a', 'WORD'))

        datas = [
            [('NUMBER', 'bar')]
        ]

        for tokens in datas:
            tokens = tokenize(tokens)

            with self.assertRaises(textparser.GrammarError) as cm:
                grammar.parse(tokens)

            self.assertEqual(cm.exception.offset, 1)

    def test_tokenizer_error(self):
        datas = [
            (2, 'hej', 'Invalid syntax at line 1, column 3: "he>>!<<j"'),
            (0, 'a\nb\n', 'Invalid syntax at line 1, column 1: ">>!<<a"'),
            (1, 'a\nb\n', 'Invalid syntax at line 1, column 2: "a>>!<<"'),
            (2, 'a\nb\n', 'Invalid syntax at line 2, column 1: ">>!<<b"')
        ]

        for offset, string, message in datas:
            with self.assertRaises(TokenizeError) as cm:
                raise TokenizeError(string, offset)

            self.assertEqual(str(cm.exception), message)

    def test_create_token_re(self):
        datas = [
            (
                [('A', r'a')],
                '(?P<A>a)'
            ),
            (
                [('A', r'b'), ('C', r'd')],
                '(?P<A>b)|(?P<C>d)'
            )
        ]

        for spec, expected_re_token in datas:
            tokens, re_token = tokenize_init(spec)
            self.assertEqual(tokens, [])
            self.assertEqual(re_token, expected_re_token)


if __name__ == '__main__':
    unittest.main()
