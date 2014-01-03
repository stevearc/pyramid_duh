""" Python 2/3 compatibility tools """
import sys

# pylint: disable=C0103,E1101

ispy3k = int(sys.version[0]) >= 3


if ispy3k:  # pragma: no cover
    string_type = str
    fuzzy_string_type = str
    bytes_types = (bytes,)
    num_types = (int, float)

    range = range
    import unittest
    unittest.TestCase.assertItemsEqual = unittest.TestCase.assertCountEqual
else:
    string_type = unicode
    fuzzy_string_type = basestring
    bytes_types = (str, bytes)
    num_types = (int, long, float)

    range = xrange


def is_string(value, strict=False):
    """ Check if a value is a string """
    if strict:
        return isinstance(value, string_type)
    return isinstance(value, fuzzy_string_type)


def is_bytes(value):
    """ Check if a value is a bytestring """
    return any(map(lambda t: isinstance(value, t), bytes_types))


def is_num(value):
    """ Check if a value is a number """
    return any(map(lambda t: isinstance(value, t), num_types))
