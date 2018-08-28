|buildstatus|_
|coverage|_

About
=====

A text parser written in the Python language.

The project has one goal, speed! See the benchmark below more details.

Project homepage: https://github.com/eerimoq/textparser

Documentation: http://textparser.readthedocs.org/en/latest

Credits
=======

- Thanks `PyParsing`_ for a user friendly interface. Many of
  ``textparser``'s class names are taken from this project.

Installation
============

.. code-block:: python

    pip install textparser

Example usage
=============

The `Hello World`_ example parses the string ``Hello, World!`` and
outputs its parse tree ``['Hello', ',', 'World', '!']``.

The script:

.. code-block:: python

   import textparser
   from textparser import Sequence


   class Parser(textparser.Parser):

       def token_specs(self):
           return [
               ('SKIP',          r'[ \r\n\t]+'),
               ('WORD',          r'\w+'),
               ('EMARK',    '!', r'!'),
               ('COMMA',    ',', r','),
               ('MISMATCH',      r'.')
           ]

       def grammar(self):
           return Sequence('WORD', ',', 'WORD', '!')


   tree = Parser().parse('Hello, World!')

   print('Tree:', tree)

Script execution:

.. code-block:: text

   $ env PYTHONPATH=. python3 examples/hello_world.py
   Tree: ['Hello', ',', 'World', '!']

Benchmark
=========

A `benchmark`_ comparing the speed of 10 JSON parsers, parsing a `276
kb file`_.

.. code-block:: text

   $ env PYTHONPATH=. python3 examples/benchmarks/json/speed.py

   Parsed 'examples/benchmarks/json/data.json' 1 time(s) in:

   PACKAGE         SECONDS   RATIO  VERSION
   textparser         0.11    100%  0.17.0
   lark (LALR)        0.28    263%  0.6.4
   funcparserlib      0.38    353%  unknown
   parsimonious       0.42    397%  unknown
   textx              0.57    536%  1.7.1
   pyparsing          0.74    696%  2.2.0
   pyleri             0.89    835%  1.2.2
   parsy              1.03    968%  1.2.0
   lark (Earley)      2.03   1903%  0.6.4
   parsita            2.54   2380%  unknown

*NOTE 1: The parsers are not necessarily optimized for
speed. Optimizing them will likely affect the measurements.*

*NOTE 2: The structure of the resulting parse trees varies and
additional processing may be required to make them fit the user
application.*

*NOTE 3: Only JSON parsers are compared. Parsing other languages may
give vastly different results.*

Contributing
============

#. Fork the repository.

#. Install prerequisites.

   .. code-block:: text

      pip install -r requirements.txt

#. Implement the new feature or bug fix.

#. Implement test case(s) to ensure that future changes do not break
   legacy.

#. Run the tests.

   .. code-block:: text

      make test

#. Create a pull request.

.. |buildstatus| image:: https://travis-ci.org/eerimoq/textparser.svg?branch=master
.. _buildstatus: https://travis-ci.org/eerimoq/textparser

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/textparser/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/textparser

.. _PyParsing: https://github.com/pyparsing/pyparsing
.. _Hello World: https://github.com/eerimoq/textparser/blob/master/examples/hello_world.py
.. _benchmark: https://github.com/eerimoq/textparser/blob/master/examples/benchmarks/json/speed.py
.. _276 kb file: https://github.com/eerimoq/textparser/blob/master/examples/benchmarks/json/data.json
