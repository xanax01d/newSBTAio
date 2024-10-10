"""TODO: Make fetch all groups (nothing)"""
import pandas as pd

df = pd.read_excel('Curs1-11.xlsx')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
column_names = df.columns
#rint(df[['МЦ391',' Unnamed: 10']])
print(column_names)
