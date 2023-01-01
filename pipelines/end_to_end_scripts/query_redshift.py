import pandas as pd
import psycopg2 

conn = psycopg2.connect(host=, \
user=, port=5439, password=,dbname= 'master')


df = pd.read_sql_query('SELECT * FROM collibrain_dataclassification.labels', conn)
df = df.dropna()
print(df.head())