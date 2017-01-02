import unittest
import mock

from haiku_cnf import search_provides, read_haikuports, firstrun

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


class TestHP(unittest.TestCase):
    @mock.patch('haiku_cnf.check_output')
    def test_haikuports(self, patched_check_output):
        ret = read_haikuports()
        patched_check_output.return_value.splitlines.assert_called_with()


class TestFirstRun(unittest.TestCase):
    @mock.patch("haiku_cnf.read_basepkgs")
    @mock.patch("haiku_cnf.get_db")
    def test_first_run(self, patched_get_db, patched_basepkgs):
        patched_get_db.return_value = {}
        patched_basepkgs.return_value = None
        firstrun()
        patched_get_db.assert_called_with()
        patched_basepkgs.assert_called_with()


