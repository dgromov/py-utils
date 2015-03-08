""" Test code for the nop test kompareity """
from collections import namedtuple
import operator
import pytest

import kompare

def test___join_key_parts():
    keys = [kompare.KeyPart("x"), kompare.KeyPart("y"), kompare.KeyPart(1, is_index=True),
            kompare.KeyPart(1)]

    actual = kompare._join_key_parts(keys)
    expected = "x.y[1].1"

    actual == expected


def test__join_empty_key_parts():
    keys = []

    actual = kompare._join_key_parts(keys)
    expected = ""

    actual == expected


def test__join_one_key_part():
    keys = [kompare.KeyPart("x")]

    actual = kompare._join_key_parts(keys)
    expected = "x"

    actual == expected


def test__join_one_key_part():
    keys = [kompare.KeyPart(1, is_index=True)]

    actual = kompare._join_key_parts(keys)
    expected = "[1]"

    actual == expected


def test_kompare_works():
    x = "someval"
    kompare.kompare(x, "someval")


def test_kompare_fails_val():
    x = "someval"
    y = "someotherval"
    with pytest.raises(AssertionError):
        kompare.kompare(x, y)


def test__kompare():
    x = "someval"
    y = "someotherval"
    expected = [([], 'Value Mismatch', x, y)]
    actual = kompare._kompare(x, y)

    actual == expected


def test__kompare_empty_dicts():
    x = "{}"
    y = "{}"

    expected = []
    actual = kompare._kompare(x, y)

    actual == expected


def test__kompare_None():
    x = None
    y = None

    expected = []
    actual = kompare._kompare(x, y)

    actual == expected


def test__kompare_dict_value():
    x = {'x': 1, 'y': {'z': "blah", 'a': "blah"}}
    y = {'x': 1, 'y': {'z': "bloop", 'a': "blah"}}

    expected = [([kompare.KeyPart('y'), kompare.KeyPart('z')], 'Value Mismatch', "blah", "bloop")]
    actual = kompare._kompare(x, y)

    actual == expected


def test__kompare_dict_key():
    x = {'x': 1, 'y': {'z': "blah", 'a': 'blah'}}
    y = {'x': 1, 'y': {'z': 'bloop', 'q': 'blah', 'a': 1}}

    expected = [([kompare.KeyPart('y')], 'Keys Differ', {'z', 'a'}, {'z', 'a', 'q'})]
    actual = kompare._kompare(x, y)

    actual == expected


def test__kompare_dict_list():
    x = {'x': 1, 'y': ['z', 'a']}
    y = {'x': 1, 'y': ['z', 'q', 'a']}

    expected = [([kompare.KeyPart('y')], 'Length Mismatch', 2, 3)]
    actual = kompare._kompare(x, y)

    actual == expected


def test__kompare_dict_namedtuple():
    repository = namedtuple("Repository", ['dir', 'tempdir', 'projects', 'apps'])
    x = {'x': 1, 'y': repository(dir="a", tempdir="", projects={}, apps={})}
    y = {'x': 1, 'y': repository(dir="b", tempdir="", projects="blah", apps={})}

    expected = [
        ([kompare.KeyPart('y'), kompare.KeyPart('projects')], 'Type Mismatch', dict, str),
        ([kompare.KeyPart('y'), kompare.KeyPart('dir')], 'Value Mismatch', "a", "b")
    ]
    actual = kompare._kompare(x, y)

    assert sorted(actual, key=operator.itemgetter(1)) == \
           sorted(expected, key=operator.itemgetter(1))


def test__kompare_dict_tuple():
    x = {'x': 1, 'y': ("a", "", {}, {})}
    y = {'x': 1, 'y': ("b", "", "blah", {})}

    expected = [
        ([kompare.KeyPart('y'), kompare.KeyPart(2, True)], 'Type Mismatch', dict, str),
        ([kompare.KeyPart('y'), kompare.KeyPart(0, True)], 'Value Mismatch', "a", "b")
    ]
    actual = kompare._kompare(x, y)

    assert sorted(actual, key=operator.itemgetter(1)) == \
           sorted(expected, key=operator.itemgetter(1))


def test__kompare_list():
    x = [1, 2, 3]
    y = [1, 2, 4]

    expected = [([kompare.KeyPart(2, is_index=True)], 'Value Mismatch', 3, 4)]
    actual = kompare._kompare(x, y)

    actual == expected
