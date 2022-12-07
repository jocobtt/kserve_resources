import pandas as pd
import psycopg2 

conn = psycopg2.connect(host='cdo-redshift-cluster-dev.c2nuq0toqpda.us-east-1.redshift.amazonaws.com', \
user='collibrain_dataclassification_rs_user', port=5439, password='8vC!ZmPuNF4eu#R4G5#V',dbname= 'master')


df = pd.read_sql_query('SELECT * FROM collibrain_dataclassification.labels', conn)
df = df.dropna()
print(df.head())