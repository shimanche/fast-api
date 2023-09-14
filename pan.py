import pandas as pd

# df = pd.read_csv('data/src/sample_header.csv')
# print(df)

async def read_csv():
  df = pd.read_csv('data/src/sample_header.csv')
  d = df.to_dict()
  return d
  