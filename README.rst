|buildstatus|_
|coverage|_

About
=====

A text parser written in the Python language.

The parser is `pretty fast`_, but not as user friendly as `PyParsing`_
and `Lark`_.

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

   from pprint import pprint

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
   token_tree = Parser().parse('Hello, World!', token_tree=True)

   print('Tree:', tree)
   print()
   print('Token tree:')
   pprint(token_tree)

Script execution:

.. code-block:: text

   $ env PYTHONPATH=. python3 examples/hello_world.py
   Tree: ['Hello', ',', 'World', '!']

   Token tree:
   [Token(kind='WORD', value='Hello', offset=0),
    Token(kind=',', value=',', offset=5),
    Token(kind='WORD', value='World', offset=7),
    Token(kind='!', value='!', offset=12)]

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

.. _pretty fast: https://github.com/eerimoq/textparser/blob/master/examples/benchmarks/json/cpu.py#L12-L25
.. _PyParsing: https://github.com/pyparsing/pyparsing
.. _Lark: https://github.com/lark-parser/lark
.. _Hello World: https://github.com/eerimoq/textparser/blob/master/examples/hello_world.py
