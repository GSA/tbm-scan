from datetime import datetime, timedelta
import os
import sys
import unittest

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from tbm_scan import get_dates

class EndToEndTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_get_dates(self):
        now_minus_two = datetime.utcnow() - timedelta(2)
        now_minus_two = now_minus_two.strftime("%Y%m%d")
        result = get_dates()
        expected = [now_minus_two]
        self.assertEqual(result, expected)

    def test_get_dates_range(self):
        result = get_dates(start_date='2019-05-01', end_date='2019-05-03')
        expected = ['20190501', '20190502', '20190503']
        self.assertCountEqual(result, expected)

if __name__ == '__main__':
    unittest.main()