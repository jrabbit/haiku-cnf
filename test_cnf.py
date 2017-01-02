import unittest
import mock

from haiku_cnf import search_provides

class TestPkgmanHooks(unittest.TestCase):
    @mock.patch('haiku_cnf.check_output')
    def test_search_provides(self, patched_check_output):
        pkgman_out = """Status  Name        Description                                              
-----------------------------------------------------------------------------
        postgresql  A powerful, open source object-relational database system"""
        # > pkgman search postgre -D
        pkgman_details = """Repository  Name               Version       Arch    
-----------------------------------------------------
HaikuPorts  postgresql         9.3.5-2       x86_gcc2
"""
        patched_check_output.return_value = pkgman_details
        ret = search_provides("pg")
        # expected = {'status': False, 'name': 'postgresql', 'description': "A powerful, open source object-relational database system"}
        expected = {'name': 'postgresql', 'repo': 'HaikuPorts'}
        self.assertEqual(ret, [expected])

    @mock.patch('haiku_cnf.check_output')
    def test_search_provides_bogus(self, patched_check_output):
        patched_check_output.return_value = "No matching packages found."
        ret = search_provides("foobarbaz")
        expected = None
        self.assertEqual(ret, expected)

