import pandas as pd
import re

pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1600)

df = pd.read_csv('lib/temp.csv')
print(df['price'].count(), 'total')

df['brand'] = df['brand'].str.lower()

df['engine'] = df['engine'].apply(lambda x: re.sub(' ', '', x))
df['engine'] = df['engine'].apply(lambda x: int(x))

df['mileage'] = df['mileage'].apply(lambda x: re.sub(' ', '', x))
df['mileage'] = df['mileage'].apply(lambda x: int(x))

# conditions

search_for = ['klasa s']
df = df[df['brand'].str.contains(('|'.join(search_for)), regex=True)]
df = df[(df['year'] < 2006) & (df['year'] > 1997)]
df = df[(df['engine'] > 4965)]

print(df['price'].count(), 'offers')

print(df[['price', 'brand', 'year', 'engine', 'url']].sort_values(by='price', ascending=True))

print(df['brand'].value_counts().head(5))
print(df['year'].value_counts().head(5))
print(df['engine'].value_counts().head(5))

print('median price', round((df['price'].median()), 2))
print('mean price', round((df['price'].mean()), 2))