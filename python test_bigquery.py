from main import load_from_bigquery

df = load_from_bigquery()

print(df.head())
print('Rows:', len(df))