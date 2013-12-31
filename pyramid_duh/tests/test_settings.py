""" Tests for settings utils """

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest

from pyramid_duh.settings import asdict


class TestAsDict(unittest.TestCase):

    """ Tests for asdict """

    def test_default(self):
        """ If provided value is a dict, return that """
        self.assertEqual(asdict({}), {})

    def test_default_none(self):
        """ If provided value is None, return {} """
        self.assertEqual(asdict(None), {})

    def test_convert(self):
        """ Convert a string to a dict """
        setting = """
        a = b
        c=d
        """
        data = {
            'a': 'b',
            'c': 'd',
        }
        self.assertEqual(asdict(setting), data)

    def test_convert_with_equals(self):
        """ Properly converts strings that have multiple equals signs """
        setting = """
        a = KpxYAw==
        b = 1+2=3
        """
        data = {
            'a': 'KpxYAw==',
            'b': '1+2=3',
        }
        self.assertEqual(asdict(setting), data)

    def test_convert_value(self):
        """ Run a function on dict values """
        setting = """
        foo = 2
        bar = 5
        """
        data = {
            'foo': 2,
            'bar': 5,
        }
        self.assertEqual(asdict(setting, int), data)
