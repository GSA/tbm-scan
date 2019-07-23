import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__) ) ) )
from utils.writer import transform_data


class WriterTestCase(unittest.TestCase):
    '''
    Test cases for functions in utils/get_nightly_data.py
    '''

    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_transform_data(self):
        data = ('20190501',
                {'PRESOL': [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 1, 'b': 2, 'c': 3}],
                'MOD': [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 1, 'b': 2, 'c': 3, 'd': 1}]}
        )
        result = transform_data(data)
        expected = [ {'notice type': 'PRESOL', 'fbo date': '20190501', 'a': 1, 'b': 2},
                     {'notice type': 'PRESOL', 'fbo date': '20190501', 'a': 3, 'b': 4},
                     {'notice type': 'PRESOL', 'fbo date': '20190501', 'a': 1, 'b': 2, 'c': 3},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'a': 1, 'b': 2},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'a': 3, 'b': 4},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'a': 1, 'b': 2, 'c': 3, 'd': 1}]
        self.assertEqual(result, expected)