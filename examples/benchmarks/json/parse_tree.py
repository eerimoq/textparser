#!/usr/bin/env python

"""Compare the parse tree of a few JSON parsers.

Example execution:

$ env PYTHONPATH=. python3 examples/benchmarks/json/parse_tree.py
-----------------------------------------------------------------

Input string between BEGIN and END:

BEGIN
[
  "foo",
  {
    "bar": [
      1,
      2,
      3
    ]
  }
]
END

textparser:
['[', [['"foo"', ['{', [[['"bar"', ':', ['[', [['1', '2', '3']], ']']]]], '}']]], ']']

lark_lalr:
Tree(list, [Tree(string, [Token(ESCAPED_STRING, '"foo"')]), Tree(dict, [Tree(pair, [Tree(string, [Token(ESCAPED_STRING, '"bar"')]), Tree(list, [Token(SIGNED_NUMBER, '1'), Token(SIGNED_NUMBER, '2'), Token(SIGNED_NUMBER, '3')])])])])

lark_earley:
Tree(list, [Tree(string, [Token(ESCAPED_STRING, '"foo"')]), Tree(dict, [Tree(pair, [Tree(string, [Token(ESCAPED_STRING, '"bar"')]), Tree(list, [Token(SIGNED_NUMBER, '1'), Token(SIGNED_NUMBER, '2'), Token(SIGNED_NUMBER, '3')])])])])

pyparsing:
[['"foo"', [['"bar"', [1, 2, 3]]]]]

parsita:
Success(['foo', [['bar', ['1', '2', '3']]]])

funcparserlib:
('"foo"', [('"bar"', ('1', ['2', '3']), [])])

parsy:
['foo', [('bar', ['1', '2', '3'])]]

parsimonious:
<Node called "json_file" matching "[
  "foo",
  {
    "bar": [
      1,
      2,
      3
    ]
  }
]
">
    <Node matching "">
    <Node called "json" matching "[
      "foo",
      {
        "bar": [
          1,
          2,
          3
        ]
      }
    ]">
        <Node called "array" matching "[
          "foo",
          {
            "bar": [
              1,
              2,
              3
            ]
          }
        ]">
            <Node matching "[">
            <Node matching "
              "foo",
              {
                "bar": [
                  1,
                  2,
                  3
                ]
              }
            ">
                <Node called "values" matching "
                  "foo",
                  {
                    "bar": [
                      1,
                      2,
                      3
                    ]
                  }
                ">
                    <Node matching "
                      "foo",
                      ">
                        <Node called "value_and_comma" matching "
                          "foo",
                          ">
                            <Node called "value" matching "
                              "foo"">
                                <Node matching "
                                  ">
                                    <RegexNode called "ws" matching "
                                      ">
                                <Node matching ""foo"">
                                    <RegexNode called "string" matching ""foo"">
                                <Node matching "">
                            <Node called "comma" matching ",
                              ">
                                <Node matching "">
                                <Node matching ",">
                                <Node matching "
                                  ">
                                    <RegexNode called "ws" matching "
                                      ">
                    <Node called "value" matching "{
                        "bar": [
                          1,
                          2,
                          3
                        ]
                      }
                    ">
                        <Node matching "">
                        <Node matching "{
                            "bar": [
                              1,
                              2,
                              3
                            ]
                          }">
                            <Node called "object" matching "{
                                "bar": [
                                  1,
                                  2,
                                  3
                                ]
                              }">
                                <Node matching "{">
                                <Node matching "
                                    "bar": [
                                      1,
                                      2,
                                      3
                                    ]
                                  ">
                                    <Node called "members" matching "
                                        "bar": [
                                          1,
                                          2,
                                          3
                                        ]
                                      ">
                                        <Node matching "">
                                        <Node called "member" matching "
                                            "bar": [
                                              1,
                                              2,
                                              3
                                            ]
                                          ">
                                            <Node matching "
                                                ">
                                                <RegexNode called "ws" matching "
                                                    ">
                                            <RegexNode called "string" matching ""bar"">
                                            <Node matching "">
                                            <Node matching ":">
                                            <Node called "value" matching " [
                                                  1,
                                                  2,
                                                  3
                                                ]
                                              ">
                                                <Node matching " ">
                                                    <RegexNode called "ws" matching " ">
                                                <Node matching "[
                                                      1,
                                                      2,
                                                      3
                                                    ]">
                                                    <Node called "array" matching "[
                                                          1,
                                                          2,
                                                          3
                                                        ]">
                                                        <Node matching "[">
                                                        <Node matching "
                                                              1,
                                                              2,
                                                              3
                                                            ">
                                                            <Node called "values" matching "
                                                                  1,
                                                                  2,
                                                                  3
                                                                ">
                                                                <Node matching "
                                                                      1,
                                                                      2,
                                                                      ">
                                                                    <Node called "value_and_comma" matching "
                                                                          1,
                                                                          ">
                                                                        <Node called "value" matching "
                                                                              1">
                                                                            <Node matching "
                                                                                  ">
                                                                                <RegexNode called "ws" matching "
                                                                                      ">
                                                                            <Node matching "1">
                                                                                <RegexNode called "number" matching "1">
                                                                            <Node matching "">
                                                                        <Node called "comma" matching ",
                                                                              ">
                                                                            <Node matching "">
                                                                            <Node matching ",">
                                                                            <Node matching "
                                                                                  ">
                                                                                <RegexNode called "ws" matching "
                                                                                      ">
                                                                    <Node called "value_and_comma" matching "2,
                                                                          ">
                                                                        <Node called "value" matching "2">
                                                                            <Node matching "">
                                                                            <Node matching "2">
                                                                                <RegexNode called "number" matching "2">
                                                                            <Node matching "">
                                                                        <Node called "comma" matching ",
                                                                              ">
                                                                            <Node matching "">
                                                                            <Node matching ",">
                                                                            <Node matching "
                                                                                  ">
                                                                                <RegexNode called "ws" matching "
                                                                                      ">
                                                                <Node called "value" matching "3
                                                                    ">
                                                                    <Node matching "">
                                                                    <Node matching "3">
                                                                        <RegexNode called "number" matching "3">
                                                                    <Node matching "
                                                                        ">
                                                                        <RegexNode called "ws" matching "
                                                                            ">
                                                        <Node matching "]">
                                                <Node matching "
                                                  ">
                                                    <RegexNode called "ws" matching "
                                                      ">
                                <Node matching "}">
                        <Node matching "
                        ">
                            <RegexNode called "ws" matching "
                            ">
            <Node matching "]">
    <Node matching "
    ">
        <RegexNode called "ws" matching "
        ">

pyleri:
<pyleri.noderesult.NodeResult object at 0x7fb4596a2480>

textx:
<textx:Array instance at 0x7fb4596deeb8>
$

"""

from __future__ import print_function

from parsers import textparser_json
from parsers import lark_json
from parsers import pyparsing_json
from parsers import funcparserlib_json
from parsers import parsimonious_json
from parsers import textx_json

try:
    from parsers import parsita_json
except:

    class parsita_json(object):

        @staticmethod
        def parse(_json_string):
            return 'Import failed!'

try:
    from parsers import parsy_json
except:
    class parsy_json(object):

        @staticmethod
        def parse(_json_string):
            return 'Import failed!'

try:
    from parsers import pyleri_json
except:
    class pyleri_json(object):

        @staticmethod
        def parse(_json_string):
            return 'Import failed!'


def parse(string):
    results = [
        ('textparser', textparser_json.parse(string)),
        ('lark_lalr', lark_json.parse_lalr(string)),
        ('lark_earley', lark_json.parse_earley(string)),
        ('pyparsing', pyparsing_json.parse(string)),
        ('parsita', parsita_json.parse(string)),
        ('funcparserlib', funcparserlib_json.parse(string)),
        ('parsy', parsy_json.parse(string)),
        ('parsimonious', parsimonious_json.parse(string)),
        ('pyleri', pyleri_json.parse(string)),
        ('textx', textx_json.parse(string))
    ]

    print('-----------------------------------------------------------------')
    print()
    print('Input string between BEGIN and END:')
    print()
    print('BEGIN')
    print(string, end='')
    print('END')
    print()

    for parser, parse_tree in results:
        print('{}:'.format(parser))
        print(parse_tree)
        print()


JSON_STRING = '''\
[
  "foo",
  {
    "bar": [
      1,
      2,
      3
    ]
  }
]
'''


parse(JSON_STRING)
