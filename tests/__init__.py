""" Tests """
import six

if six.PY3:  # pragma: no cover
    import unittest
    # pylint: disable=E1101
    unittest.TestCase.assertItemsEqual = unittest.TestCase.assertCountEqual
