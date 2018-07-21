import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import logging

import textparser


class TextParserDatabaseTest(unittest.TestCase):

    maxDiff = None

    def test_sequence(self):
        pass


# This file is not '__main__' when executed via 'python setup.py3
# test'.
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    unittest.main()
