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

    def test_transform_data_field_filter(self):
        data = ('20190501',
                {'PRESOL': [{'AGENCY': 1, 'b': 2}, {'AGENCY': 3, 'b': 4}, {'AGENCY': 1, 'b': 2, 'c': 3}],
                'MOD': [{'AGENCY': 1, 'b': 2}, {'AGENCY': 3, 'b': 4}, {'AGENCY': 1, 'b': 2, 'c': 3, 'd': 1}]}
        )
        result = transform_data(data, field_filter = True)
        expected = [ {'notice type': 'PRESOL', 'fbo date': '20190501', 'AGENCY': 1},
                     {'notice type': 'PRESOL', 'fbo date': '20190501', 'AGENCY': 3},
                     {'notice type': 'PRESOL', 'fbo date': '20190501', 'AGENCY': 1},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'AGENCY': 1},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'AGENCY': 3},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'AGENCY': 1}]
        self.assertEqual(result, expected)

    def test_transform_data(self):
        data = ('20190501',
                {'PRESOL': [{'AGENCY': 1, 'b': 2}, {'AGENCY': 3, 'b': 4}, {'AGENCY': 1, 'b': 2}],
                'MOD': [{'AGENCY': 1, 'b': 2}, {'AGENCY': 3, 'b': 4}, {'AGENCY': 1, 'b': 2}]}
        )
        result = transform_data(data)
        expected = [ {'notice type': 'PRESOL', 'fbo date': '20190501', 'AGENCY': 1, 'b':2},
                     {'notice type': 'PRESOL', 'fbo date': '20190501', 'AGENCY': 3, 'b':4},
                     {'notice type': 'PRESOL', 'fbo date': '20190501', 'AGENCY': 1, 'b':2},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'AGENCY': 1, 'b':2},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'AGENCY': 3, 'b':4},
                     {'notice type': 'MOD', 'fbo date': '20190501', 'AGENCY': 1, 'b':2}]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()