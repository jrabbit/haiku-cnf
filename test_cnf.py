import unittest
import mock

from haiku_cnf import search_provides

class TestPkgmanHooks(unittest.TestCase):
    @mock.patch('subprocess.check_output')
    def test_search_provides(self, patched_check_output):
        pkgman_out = """Status  Name        Description                                              
-----------------------------------------------------------------------------
        postgresql  A powerful, open source object-relational database system"""

        patched_check_output.return_value = pkgman_out
        ret = search_provides("pg")
        expected = {'status': False, 'name': 'postgresql', 'description': "A powerful, open source object-relational database system"}
        self.assertEqual(ret, [expected])

    @mock.patch('subprocess.check_output')
    def test_search_provides_bogus(self, patched_check_output):
        patched_check_output.return_value = "No matching packages found."
        ret = search_provides("foobarbaz")
        expected = None
        self.assertEqual(ret, expected)

