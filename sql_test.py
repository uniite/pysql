import unittest
from pysql import *

class SQLParserTests(unittest.TestCase):
    def test_scanner(self):
        """ Just a quick test of the scanner for now. """
        # TODO: Add more punctuation/syntax tests
        # TODO: Do case-sensitivity checking for keywords
        st = SQLStatement("SELECT `name`, location FROM people WHERE (name='Jon') AND location = \"manhattan\";")
        self.assertEqual(
            ([('keyword', 'SELECT'), ('identifier', '`name`'), ('operator', ','),
              ('identifier', 'location'), ('keyword', 'FROM'),
              ('identifier', 'people'), ('keyword', 'WHERE'), ('operator', '('),
              ('identifier', 'name'), ('operator', '='), ('value', "'Jon'"),
              ('operator', ')'), ('operator', 'AND'), ('identifier', 'location'),
              ('operator', '='), ('value', '"manhattan"'), ('operator', ';')], ''),
            st.scan())



if __name__ == '__main__':
    unittest.main()
