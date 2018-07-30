"""Based on
https://gist.githubusercontent.com/reclosedev/5222560/raw/5e97cf7eb62c3a3671885ec170577285e891f7d5/parsimonious_json.py

"""

import timeit

from parsimonious.grammar import Grammar


grammar = Grammar(
    r"""
    json_file = ws? json ws?
    json = object / array

    object = "{" members? "}"
    members = member_and_comma* member
    member_and_comma = member comma
    member = ws? string ws? ":" value

    array = "[" values? "]"
    values = value_and_comma* value
    value_and_comma = value comma

    value = ws? (true / false / object / array / number / string / null) ws?
    true = "true"
    false = "false"
    null = "null"
    number = ~r"-?(0|([1-9][0-9]*))(\.[0-9]+)?([Ee][+-][0-9]+)?"
    string = ~"\"[^\"\\\\]*(?:\\\\.[^\"\\\\]*)*\""is
    ws = ~r"\s+"
    comma = ws? "," ws?
    """)


def parse_time(json_string, iterations):
    def _parse():
        grammar.parse(json_string)

    return timeit.timeit(_parse, number=iterations)


def parse(json_string):
    return grammar.parse(json_string)


def version():
    return 'unknown'
