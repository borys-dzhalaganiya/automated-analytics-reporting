import pandas as pd
import numpy as np

n = 10000
status_probabilities = [0.3, 0.7]

user_id = np.arange(1, n + 1)
sources = np.random.choice(['google', 'facebook', 'organic', 'affiliates'], size=n)
status = np.random.choice(['issued', 'rejected'], size=n, p=status_probabilities)
amount = np.random.randint(1000, 20001, size=n)

start_date = pd.Timestamp('2026-08-01')
days = np.random.randint(0, 61, size=n)
created_at = start_date + pd.to_timedelta(days, unit='D')

df = pd.DataFrame(
    {'user_id': user_id,
    'source': sources,
    'status': status,
    'amount': amount,
    'created_at': created_at}
    )


df.to_csv('data/applications.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')
print('CSV successfully saved')