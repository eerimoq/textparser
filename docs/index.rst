.. textparser documentation master file, created by
   sphinx-quickstart on Sat Apr 25 11:54:09 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2

Text parser
===========

.. include:: ../README.rst

The parser class
================

.. autoclass:: textparser.Parser
    :members:

Building the grammar
====================

The grammar built by combining the classes below and strings.

Here is a fictitious example grammar:

.. code-block:: python

   grammar = Sequence(
       'BEGIN',
       Optional(choice('IF', Sequence(ZeroOrMore('NUMBER')))),
       OneOrMore('WORD', end=Sequence('WORD', 'NUMBER')),
       Any(),
       DelimitedList('WORD', delim=':'),
       'END')

.. autoclass:: textparser.Sequence
    :members:

.. autoclass:: textparser.Choice
    :members:

.. autoclass:: textparser.ChoiceDict
    :members:

.. autofunction:: textparser.choice

.. autoclass:: textparser.ZeroOrMore
    :members:

.. autoclass:: textparser.ZeroOrMoreDict
    :members:

.. autoclass:: textparser.OneOrMore
    :members:

.. autoclass:: textparser.OneOrMoreDict
    :members:

.. autoclass:: textparser.DelimitedList
    :members:

.. autoclass:: textparser.Optional
    :members:

.. autoclass:: textparser.Any
    :members:

.. autoclass:: textparser.Not
    :members:

.. autoclass:: textparser.NoMatch
    :members:

.. autoclass:: textparser.Tag
    :members:

.. autoclass:: textparser.Forward
    :members:

.. autoclass:: textparser.Repeated
    :members:

.. autoclass:: textparser.RepeatedDict
    :members:

.. autoclass:: textparser.Pattern
    :members:

Exceptions
==========

.. autoclass:: textparser.Error
    :members:

.. autoclass:: textparser.ParseError
    :members:

.. autoclass:: textparser.TokenizeError
    :members:

.. autoclass:: textparser.GrammarError
    :members:

Utility functions
=================

.. autofunction:: textparser.markup_line

.. autofunction:: textparser.tokenize_init
