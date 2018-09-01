#!/usr/bin/env python

"""A benchmark comparing the speed of 10 parsers.

Test data generated with https://www.json-generator.com.

Example execution:

$ env PYTHONPATH=. python3 examples/benchmarks/json/speed.py
Parsed 'examples/benchmarks/json/data.json' 1 time(s) in:

PACKAGE         SECONDS   RATIO  VERSION
textparser         0.10    100%  0.17.0
parsimonious       0.17    174%  unknown
lark (LALR)        0.25    253%  0.6.4
funcparserlib      0.33    335%  unknown
textx              0.51    520%  1.7.1
pyparsing          0.65    654%  2.2.0
pyleri             0.78    786%  1.2.2
parsy              0.92    931%  1.2.0
lark (Earley)      1.80   1816%  0.6.4
parsita            2.22   2251%  unknown
$

"""

from __future__ import print_function

import os

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
        def parse_time(_json_string, _iterations):
            return float('inf')

        @staticmethod
        def version():
            return 'unknown'

try:
    from parsers import parsy_json
except:
    class parsy_json(object):

        @staticmethod
        def parse_time(_json_string, _iterations):
            return float('inf')

        @staticmethod
        def version():
            return 'unknown'

try:
    from parsers import pyleri_json
except:
    class pyleri_json(object):

        @staticmethod
        def parse_time(_json_string, _iterations):
            return float('inf')

        @staticmethod
        def version():
            return 'unknown'


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_JSON = os.path.relpath(os.path.join(SCRIPT_DIR, 'data.json'))

ITERATIONS = 1


with open(DATA_JSON, 'r') as fin:
    JSON_STRING = fin.read()

textparser_time = textparser_json.parse_time(JSON_STRING, ITERATIONS)
lark_lalr_time = lark_json.parse_time_lalr(JSON_STRING, ITERATIONS)
lark_earley_time = lark_json.parse_time_earley(JSON_STRING, ITERATIONS)
pyparsing_time = pyparsing_json.parse_time(JSON_STRING, ITERATIONS)
parsita_time = parsita_json.parse_time(JSON_STRING, ITERATIONS)
funcparserlib_time = funcparserlib_json.parse_time(JSON_STRING, ITERATIONS)
parsy_time = parsy_json.parse_time(JSON_STRING, ITERATIONS)
parsimonious_time = parsimonious_json.parse_time(JSON_STRING, ITERATIONS)
pyleri_time = pyleri_json.parse_time(JSON_STRING, ITERATIONS)
textx_time = textx_json.parse_time(JSON_STRING, ITERATIONS)

# Parse comparison output.
measurements = [
    ('textparser', textparser_time, textparser_json.version()),
    ('lark (LALR)', lark_lalr_time, lark_json.version()),
    ('lark (Earley)', lark_earley_time, lark_json.version()),
    ('pyparsing', pyparsing_time, pyparsing_json.version()),
    ('parsita', parsita_time, parsita_json.version()),
    ('funcparserlib', funcparserlib_time, funcparserlib_json.version()),
    ('parsy', parsy_time, parsy_json.version()),
    ('parsimonious', parsimonious_time, parsimonious_json.version()),
    ('pyleri', pyleri_time, pyleri_json.version()),
    ('textx', textx_time, textx_json.version())
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print("Parsed '{}' {} time(s) in:".format(DATA_JSON, ITERATIONS))
print()
print('PACKAGE         SECONDS   RATIO  VERSION')

for package, seconds, version in measurements:
    try:
        ratio = int(round(100 * (seconds / textparser_time), 0))
        ratio = '{:5}'.format(ratio)
    except OverflowError:
        ratio = '  inf'

    print('{:14s}  {:7.02f}  {}%  {}'.format(package,
                                             seconds,
                                             ratio,
                                             version))
