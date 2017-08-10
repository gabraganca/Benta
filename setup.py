"""
Setup file for installation
"""
import os
from setuptools import setup

def read(fname):
    """
     Utility function to read the README file.  Used for the long_description.
     It's nice, because now 1) we have a top level README file and 2) it's
     easier to type in the README file than to put a raw string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Benta",
    version="0.0.1",
    author="Gustavo Braganca",
    author_email="ga.braganca@gmail.com",
    description=("My personal Python cookbook/library."),
    license="MIT",
    keywords="cookbook",
    url="https://github.com/gabraganca/Benta",
    long_description=read('README.md'),
    packages=['benta']
)
