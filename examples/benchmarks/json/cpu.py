#!/usr/bin/env python

"""A performance example comparing the performance of four parsers.

Test data generated with https://www.json-generator.com.

Example execution:

$ env PYTHONPATH=. python3 examples/benchmarks/json/cpu.py
Parsing 'examples/benchmarks/json/data.json' 1 time(s) per parser. This may take a few seconds.

Parsing 'examples/benchmarks/json/data.json' 1 time(s) took:

PACKAGE        SECONDS
textparser     0.099870
lark (LALR)    0.252110
funcparserlib  0.349336
parsimonious   0.386092
pyparsing      0.720664
parsy          0.940929
lark (Earley)  1.823468
parsita        2.435160
$

"""

from __future__ import print_function

import os

from parsers import textparser_json
from parsers import lark_json
from parsers import pyparsing_json
from parsers import funcparserlib_json
from parsers import parsimonious_json

try:
    from parsers import parsita_json
except:
    class parsita_json(object):

        @staticmethod
        def parse(_json_string, _iterations):
            return float('inf')

try:
    from parsers import parsy_json
except:
    class parsy_json(object):

        @staticmethod
        def parse(_json_string, _iterations):
            return float('inf')


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_JSON = os.path.relpath(os.path.join(SCRIPT_DIR, 'data.json'))

ITERATIONS = 1


with open(DATA_JSON, 'r') as fin:
    JSON_STRING = fin.read()


print("Parsing '{}' {} time(s) per parser. This may take a few seconds.".format(
    DATA_JSON,
    ITERATIONS))

textparser_time = textparser_json.parse(JSON_STRING, ITERATIONS)
lark_lalr_time = lark_json.parse_lalr(JSON_STRING, ITERATIONS)
lark_earley_time = lark_json.parse_earley(JSON_STRING, ITERATIONS)
pyparsing_time = pyparsing_json.parse(JSON_STRING, ITERATIONS)
parsita_time = parsita_json.parse(JSON_STRING, ITERATIONS)
funcparserlib_time = funcparserlib_json.parse(JSON_STRING, ITERATIONS)
parsy_time = parsy_json.parse(JSON_STRING, ITERATIONS)
parsimonious_time = parsimonious_json.parse(JSON_STRING, ITERATIONS)

# Parse comparison output.
measurements = [
    ('textparser', textparser_time),
    ('lark (LALR)', lark_lalr_time),
    ('lark (Earley)', lark_earley_time),
    ('pyparsing', pyparsing_time),
    ('parsita', parsita_time),
    ('funcparserlib', funcparserlib_time),
    ('parsy', parsy_time),
    ('parsimonious', parsimonious_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print("Parsing '{}' {} time(s) took:".format(DATA_JSON, ITERATIONS))
print()
print('PACKAGE        SECONDS')

for package, seconds in measurements:
    print('{:14s} {:f}'.format(package, seconds))
