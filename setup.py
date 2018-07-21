#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
import re


def find_version():
    return re.search(r"^__version__ = '(.*)'$",
                     open('textparser.py', 'r').read(),
                     re.MULTILINE).group(1)


setup(name='textparser',
      version=find_version(),
      description='Text parser.',
      long_description=open('README.rst', 'r').read(),
      author='Erik Moqvist',
      author_email='erik.moqvist@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords=['parser'],
      url='https://github.com/eerimoq/textparser',
      py_modules=['textparser'],
      test_suite="tests")
