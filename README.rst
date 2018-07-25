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

The `hello world`_ example parses the string ``Hello, World!`` and
outputs its parse tree ``['Hello', ',', 'World', '!']``.

The script:

.. code-block:: python

   import textparser
   from textparser import Sequence
   from textparser import Grammar


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
           return Grammar(Sequence('WORD', ',', 'WORD', '!'))


   tree = Parser().parse('Hello, World!')

   print('Tree:', tree)

Executing the script:

.. code-block::

   $ python3 examples/hello_world.py
   Tree: ['Hello', ',', 'World', '!']
   $

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

.. _pretty fast: https://github.com/eerimoq/textparser/blob/master/examples/benchmarks/json/main.py#L15-L25
.. _PyParsing: https://github.com/pyparsing/pyparsing
.. _Lark: https://github.com/lark-parser/lark
.. _hello world: https://github.com/eerimoq/textparser/blob/master/examples/hello_world.py
