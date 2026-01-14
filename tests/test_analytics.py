
import unittest
import pandas as pd
import numpy as np
from src.analytics import aggregate_time_series, aggregate_state_stats

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        # Create dummy data for testing
        self.df = pd.DataFrame({
            'state': ['StateA', 'StateB', 'StateC', 'StateA'],
            'enc_count': [100, 200, 150, 110],
            'upd_count': [50, 100, 75, 55],
            'date': pd.to_datetime(['2025-01-01', '2025-01-01', '2025-01-01', '2025-01-02']),
            'pincode': [111, 222, 333, 111] # Should be ignored if we choose cols right
        })
        self.numeric_cols = ['enc_count', 'upd_count']

    def test_aggregate_time_series(self):
        """Test aggregation by date."""
        result = aggregate_time_series(self.df, self.numeric_cols)
        self.assertEqual(len(result), 2) # Two distinct dates
        # Check sums for 2025-01-01 (StateA:100, StateB:200, StateC:150 = 450)
        row1 = result[result['date'] == '2025-01-01'].iloc[0]
        self.assertEqual(row1['enc_count'], 450)
        self.assertEqual(row1['upd_count'], 225)

    def test_aggregate_state_stats(self):
        """Test aggregation by state."""
        result = aggregate_state_stats(self.df, self.numeric_cols)
        self.assertEqual(len(result), 3) # 3 states
        # Check StateA sum (100 + 110 = 210)
        row_a = result[result['state'] == 'StateA'].iloc[0]
        self.assertEqual(row_a['enc_count'], 210)
        self.assertTrue('Total' in result.columns)
        self.assertEqual(row_a['Total'], 210 + 105) # 105 is upd_count sum (50+55)

    def test_dummy_pass(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
