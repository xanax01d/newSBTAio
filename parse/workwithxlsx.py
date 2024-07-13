#TODO: Make fetch all groups (now maked nothing)
import pandas as pd
df = pd.read_excel('Curs1-11.xlsx')
pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows', None)
print(df[['МЦ391',' Unnamed: 10']])
