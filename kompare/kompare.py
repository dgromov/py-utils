from collections import Iterable

class KeyPart():
    """
    This class describes one component of a key in a dictionary.

    """
    def __init__(self, val, is_index=False):
        """
        Creates a KeyPart object

        :param str val: The name of the key
        :param bool is_index: If the key is an index
        :return: A KeyPart object
        :rtype: KeyPart
        """
        self.value = val
        self.is_index = is_index

    def __eq__(self, other):
        """
        Equality operator for KeyPart

        :param KeyPart other: Another KeyPart object
        :return: If the other KeyPart is equal to this one.
        """
        return self.value == other.value and \
            self.is_index == other.is_index

    def __repr__(self):
        """
        :return: A string representation of a KeyPart
        """
        return "value: {} -- is_index: {}".format(self.value, self.is_index)


def _join_key_parts(key_parts):
    """
    Given a list of KeyParts, create a string representation for showing in error messages.

    E.g. _join_key_parts([KeyPart('x'), KeyPart('y'), KeyPart(1, True)) => x.y[1]

    :param list[KeyPart] key_parts: A list of keyparts
    :return: The string representation of all the keyparts
    :rtype: str
    """
    total_key = ""
    for part in key_parts:
        if part.is_index:
            total_key += "[{}]".format(str(part.value))
        else:
            total_key += "{}{}".format("." if total_key != "" else "", part.value)

    return total_key


def _diff_message(key_parts, message, actual, expected):
    """
    Generates a diff message for the given key parts and values

    :param list[KeyParts] key_parts: The KeyParts at which the actual and expected values can be
    found.
    :param str message: The diff message
    :param obj actual: The actual value
    :param obj expected: The expected value
    :return: A string describing the difference between the two objects found at the key.
    :rtype: str
    """
    if not key_parts:
        key_parts = [KeyPart("TOP LEVEL")]

    return "{}: {}.\n\tactual: {}\n\texpected: {}".format(_join_key_parts(key_parts),
                                                                 message, actual, expected)

def _kompare(left, right):
    """
    Given two objects, left and right, which represent the actual and expected object respectively,
    returns a list of tuples describing the differences between the two objects.

    Some notes:
        - This function handles namedtuples by digging into their underlying dict representations.
        - subclasses of tuple, that are not namedtuples may not work
        - Ignores order of key appearance in dicts but cares for iterables

    example result:

    [
        ([KeyPart('x')], 'Value Mismatch', 1, 2),
        ([KeyPart('y'), KeyPart(1, True)], 'Type Mismatch', dict, int)
    ]

    :param obj left: The actual object
    :param obj right: The expected object
    :return: A list of tuples describing the differences between the left and right objects
    :rtype: List of (List[KeyType], str, obj, obj)
    """

    # Pytest thing. Without this, it will show that the error occurred in this function. That
    # isn't particularly useful.
    __tracebackhide__ = True

    diffs = []

    def difference(level, actual, expected):
        if type(actual) != type(expected):
            diffs.append((level, "Type Mismatch", type(actual), type(expected)))
            return

        # TODO: Make this less hacky. If you give this function something that is a
        # subclass of tuple but is not a namedtuple, this may not work.
        if isinstance(actual, tuple) and type(actual) != tuple:
            try:
                actual = vars(actual)
                expected = vars(expected)
            except TypeError:
                try:
                    actual = vars(super(type(actual), actual))
                    expected = vars(super(type(expected), expected))
                except:
                    pass

        if isinstance(actual, dict):
            actual_keys = set(actual.keys())
            expected_keys = set(expected.keys())

            if len(actual_keys ^ expected_keys) > 0:
                diffs.append((level, 'Keys Differ', actual_keys, expected_keys))
            else:
                for key in actual_keys:
                    difference(level + [KeyPart(key)], actual[key], expected[key])
        else:
            if isinstance(actual, Iterable) and not isinstance(actual, str):
                if len(actual) != len(expected):
                    diffs.append((level, "Length Mismatch", len(actual), len(expected)))
                else:
                    for idx, (act, exp) in enumerate(zip(actual, expected)):
                        difference(level + [KeyPart(idx, True)], act, exp)

            elif actual != expected:
                diffs.append((level, "Value Mismatch", actual, expected))

    if len(diffs) == 0:
        difference([], left, right)

    return diffs


def kompare(left, right):
    """
    The actual kompare function to be called by tests. This one formats the output of _kompare
    into diff messages and raises and error if any mismatches exist.
    :param obj left: The actual object
    :param obj right: The expected object
    :raises AssertionError: If _kompare returned any results.
    """
    diff_messages = [_diff_message(*x) for x in _kompare(left, right)]
    if len(diff_messages) > 0:
        raise AssertionError("\n" + "\n".join(diff_messages))
