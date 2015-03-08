#!/usr/bin/env python
import glob
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand
import sys
import warnings

PYTEST_ARGS = ["--junitxml=.tox/test-results.xml"]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = PYTEST_ARGS
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def get_readme():
    """ Get the README from the current directory. If there isn't one, return an empty string """
    all_readmes = sorted(glob.glob("README*"))
    if len(all_readmes) > 1:
        warnings.warn("There seems to be more than one README in this directory. Choosing the "
                      "first in lexicographic order.")
    if len(all_readmes) > 0:
        return open(all_readmes[0], 'r').read()

    warnings.warn("There doesn't seem to be a README in this directory.")
    return ""

setup(
    name="kompare2",
    version='0.1',
    url="https://github.com/dgromov/py-utils",
    author="Dmitriy Gromov",
    author_email="dmitriy.k.gromov@gmail.com",
    license="Proprietary",
    packages=find_packages(),
    cmdclass={"test": PyTest},
    install_requires=open('requirements.txt', 'r').readlines(),
    tests_require=open('requirements.testing.txt', 'r').readlines(),
    description="smart comparison function",
    long_description="\n" + get_readme()
)
