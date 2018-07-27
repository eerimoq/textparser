#!/usr/bin/env python3
#
# > env PYTHONPATH=.. python3 proto3.py
# Tree: [['syntax', '=', '"proto3"', ';'],
#  [['import', ['public'], '"foo.bar"', ';'],
#   ['option', ['java_package', []], '=', '"com.example.foo"', ';'],
#   ['option', ['java_multiple_files', []], '=', ['true'], ';'],
#   ['enum',
#    'EnumAllowingAlias',
#    ['{',
#     [['option', ['allow_alias', []], '=', ['true'], ';'],
#      ['UNKNOWN', '=', '0', [], ';'],
#      ['STARTED', '=', '1', [], ';'],
#      ['RUNNING',
#       '=',
#       '2',
#       [['[',
#         [[[['(', ['custom_option'], ')'], []], '=', '"hello world"']],
#         ']']],
#       ';']],
#     '}']],
#   ['message',
#    'outer',
#    ['{',
#     [['option', [['(', ['my_option'], ')'], [['.', 'a']]], '=', ['true'], ';'],
#      [[],
#       [[], ['int32']],
#       'old_field',
#       '=',
#       '1',
#       [['[', [[['deprecated', []], '=', ['true']]], ']']],
#       ';'],
#      ['message',
#       'inner',
#       ['{', [[[], [[], ['int64']], 'ival', '=', '2', [], ';']], '}']],
#      [['repeated'], [[], ['inner']], 'inner_message', '=', '3', [], ';'],
#      [[], [[], ['EnumAllowingAlias']], 'enum_field', '=', '4', [], ';'],
#      ['map',
#       '<',
#       'int32',
#       ',',
#       [[], ['string']],
#       '>',
#       'my_map',
#       '=',
#       '5',
#       [],
#       ';'],
#      [[], [[], ['foo', 'bar', 'Open']], 'open', '=', '6', [], ';'],
#      [[], [['.'], ['foo', 'bar', 'Close']], 'close', '=', '7', [], ';'],
#      ['oneof',
#       'test_oneof',
#       '{',
#       [[[[], ['string']], 'name', '=', '8', [], ';'],
#        [[[], ['SubMessage']], 'sub_message', '=', '9', [], ';']],
#       '}'],
#      ['reserved', [['2', '15', '9'], [['to', '11']]], ';'],
#      ['reserved', [['7'], []], ';'],
#      ['reserved', [['15'], [['to', 'max']]], ';']],
#     '}']],
#   ['service',
#    'SearchService',
#    '{',
#    [['rpc',
#      'Search',
#      '(',
#      [],
#      'SearchRequest',
#      ')',
#      'returns',
#      '(',
#      [],
#      'SearchResponse',
#      ')',
#      ';']],
#    '}']]]
#

from pprint import pformat

import textparser
from textparser import Sequence
from textparser import ZeroOrMore
from textparser import choice
from textparser import Optional
from textparser import DelimitedList
from textparser import Forward


class Parser(textparser.Parser):

    def keywords(self):
        return set([
            'syntax',
            'import',
            'public',
            'option',
            'enum',
            'bool',
            'string',
            'message',
            'rpc',
            'service',
            'returns',
            'repeated',
            'map',
            'package',
            'stream',
            'weak',
            'oneof',
            'reserved',
            'to',
            'int32',
            'int64',
            'uint32',
            'uint64',
            'sint32',
            'sint64',
            'fixed32',
            'fixed64',
            'sfixed32',
            'sfixed64',
            'true',
            'false',
            'min',
            'max'
        ])

    def token_specs(self):
        decimals = r'[0-9]+'
        exponent = r'[eE][+-]?[0-9]+'
        re_float = r'{d}\.[0-9]?({e})?|{d}({e})?|\.{d}({e})?|inf|nan'.format(
            d=decimals,
            e=exponent)

        return [
            ('SKIP',                 r'[ \r\n\t]+|//[\s\S]*?\n'),
            ('ESCAPED_STRING',       r'"(\\"|[^"])*?"'),
            ('INT',                  r'[1-9][0-9]*|0[0-7]*|0[xX][0-9a-fA-F]+'),
            ('FLOAT',                re_float),
            ('IDENT',                r'[a-zA-Z][a-zA-Z0-9_]*'),
            ('DOT',            '.',  r'\.'),
            ('COMMA',          ',',  r','),
            ('SCOLON',         ';',  r';'),
            ('EQ',             '=',  r'='),
            ('LT',             '<',  r'<'),
            ('GT',             '>',  r'>'),
            ('LBRACE',         '{',  r'\{'),
            ('RBRACE',         '}',  r'\}'),
            ('LBRACK',         '[',  r'\['),
            ('RBRACK',         ']',  r'\]'),
            ('LPAREN',         '(',  r'\('),
            ('RPAREN',         ')',  r'\)'),
            ('MISMATCH',             r'.')
        ]

    def grammar(self):
        message = Forward()
        rpc = Forward()

        ident = choice(*(list(self.keywords()) + ['IDENT']))
        full_ident = DelimitedList(ident, delim='.')

        # Constant.
        constant = choice(full_ident,
                          Sequence(Optional(choice('-', '+')), 'INT'),
                          Sequence(Optional(choice('-', '+')), 'FLOAT'),
                          'ESCAPED_STRING',
                          'true',
                          'false')

        # Syntax.
        syntax = Sequence('syntax', '=', 'ESCAPED_STRING', ';')

        # Import statement.
        import_ = Sequence('import',
                           Optional(choice('weak', 'public')),
                           'ESCAPED_STRING', ';')

        # Package.
        package = Sequence('package', full_ident, ';')

        # Option.
        option_name = Sequence(choice(ident, Sequence('(', full_ident, ')')),
                               ZeroOrMore(Sequence('.', ident)))
        option = Sequence('option', option_name, '=', constant, ';')

        # Fields.
        type_ = choice(Sequence(Optional('.'), DelimitedList(ident, '.')),
                       ident)
        field_number = 'INT'

        # Normal field.
        field_option = Sequence(option_name, '=', constant)
        field_options = DelimitedList(field_option)
        field = Sequence(Optional('repeated'),
                         type_, ident, '=', field_number,
                         Optional(Sequence('[', field_options, ']')),
                         ';')

        # Oneof and oneof field.
        oneof_field = Sequence(type_, ident, '=', field_number,
                               Optional(Sequence('[', field_options, ']')),
                               ';')
        oneof = Sequence('oneof', ident,
                         '{',
                         ZeroOrMore(choice(oneof_field, ';')),
                         '}')

        # Map field.
        key_type = choice('int32',
                          'int64',
                          'uint32',
                          'uint64',
                          'sint32',
                          'sint64',
                          'fixed32',
                          'fixed64',
                          'sfixed32',
                          'sfixed64',
                          'bool',
                          'string')
        map_field = Sequence('map', '<', key_type, ',', type_, '>',
                             ident, '=', field_number,
                             Optional(Sequence('[', field_options, ']')),
                             ';')

        # Reserved.
        field_names = DelimitedList(ident)
        ranges = Sequence(DelimitedList('INT'),
                          Optional(Sequence('to', choice('INT', 'max'))))
        reserved = Sequence('reserved', choice(ranges, field_names), ';')

        # Enum definition.
        enum_value_option = Sequence(option_name, '=', constant)
        enum_field = Sequence(
            ident, '=', 'INT',
            Optional(Sequence('[', DelimitedList(enum_value_option), ']')),
            ';')
        enum_body = Sequence('{',
                             ZeroOrMore(choice(option, enum_field, ';')),
                             '}')
        enum = Sequence('enum', ident, enum_body)

        # Message definition.
        message_body = Sequence('{',
                                ZeroOrMore(choice(field,
                                                  enum,
                                                  message,
                                                  option,
                                                  oneof,
                                                  map_field,
                                                  reserved,
                                                  ';')),
                                '}')
        message <<= Sequence('message', ident, message_body)

        # Service definition.
        service = Sequence('service', ident,
                           '{',
                           ZeroOrMore(choice(option, rpc, ';')),
                           '}')
        rpc <<= Sequence('rpc', ident,
                         '(',
                         Optional('stream'), ident,
                         ')',
                         'returns',
                         '(',
                         Optional('stream'), ident,
                         ')',
                         choice(Sequence('{',
                                         ZeroOrMore(choice(option, ';')),
                                         '}'),
                                ';'))

        # Proto file.
        proto = Sequence(syntax,
                         ZeroOrMore(choice(import_,
                                           package,
                                           option,
                                           message,
                                           enum,
                                           service,
                                           ';')))

        return proto


proto_string = '''
syntax = "proto3";

import public "foo.bar";

option java_package = "com.example.foo";
option java_multiple_files = true;

enum EnumAllowingAlias {
  option allow_alias = true;
  UNKNOWN = 0;
  STARTED = 1;
  RUNNING = 2 [(custom_option) = "hello world"];
}

message outer {
  option (my_option).a = true;
  int32 old_field = 1 [deprecated=true];
  message inner {   // Level 2
    int64 ival = 2;
  }
  repeated inner inner_message = 3;
  EnumAllowingAlias enum_field =4;
  map<int32, string> my_map = 5;
  foo.bar.Open open = 6;
  .foo.bar.Close close = 7;
  oneof test_oneof {
    string name = 8;
    SubMessage sub_message = 9;
  }
  reserved 2, 15, 9 to 11;
  reserved 7;
  reserved 15 to max;
}

service SearchService {
  rpc Search (SearchRequest) returns (SearchResponse);
}
'''

tree = Parser().parse(proto_string)

print('Tree:', pformat(tree))
