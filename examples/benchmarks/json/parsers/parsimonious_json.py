"""Based on
https://gist.github.com/goodmami/686385b4b39a3bac00fbbe78a5cda6c8, by
Michael Wayne Goodman.

"""

import timeit

from parsimonious.grammar import Grammar


grammar = Grammar(
    r"""
    Start    = ~"\s*" ( Object / Array ) ~"\s*"
    Object   = ~"{\s*" Members? ~"\s*}"
    Members  = MappingComma* Mapping
    MappingComma = Mapping ~"\s*,\s*"
    Mapping  = DQString ~"\s*:\s*" Value
    Array    = ~"\[\s*" Items? ~"\s*\]"
    Items    = ValueComma* Value
    ValueComma = Value ~"\s*,\s*"
    Value    = Object / Array / DQString
             / TrueVal / FalseVal / NullVal / Float / Integer
    TrueVal  = "true"
    FalseVal = "false"
    NullVal  = "null"
    DQString = ~"\"[^\"\\\\]*(?:\\\\.[^\"\\\\]*)*\""
    Float    = ~"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?"
    Integer  = ~"[-+]?\d+"
    """)


def parse_time(json_string, iterations):
    def _parse():
        grammar.parse(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    return grammar.parse(json_string)


def version():
    return 'unknown'
