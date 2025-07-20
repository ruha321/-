import pandas as pd

df1 = pd.read_csv('waka_manyoshu.csv')
df2 = pd.read_csv('waka_aozora.csv')
df = pd.concat([df1, df2], ignore_index=True).drop_duplicates(subset=['text'])
df.to_csv('waka.csv', index=False, encoding='utf-8')