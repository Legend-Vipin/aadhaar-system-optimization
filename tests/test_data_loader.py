import unittest
import pandas as pd
import os
from src.data_loader import clean_data

class TestDataLoader(unittest.TestCase):
    def test_clean_data_basic(self):
        # Create a mock dataframe
        data = {
            'date': ['01-01-2023', 'invalid', '02-01-2023'],
            'state': ['A', 'B', 'B'],
            'count': [10, 20, 30]
        }
        df = pd.DataFrame(data)
        
        # Run cleaning
        cleaned = clean_data(df, 'test_category')
        
        # Assertions
        self.assertEqual(len(cleaned), 2, "Should remove row with invalid date")
        self.assertTrue('YearMonth' in cleaned.columns, "Should create derived feature")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned['date']), "Date should be datetime")

if __name__ == '__main__':
    unittest.main()
