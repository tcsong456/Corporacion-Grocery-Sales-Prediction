# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 16:42:56 2025

@author: congx
"""
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.types import ByteType,ShortType,IntegerType
from pyspark.sql.functions import col,expr,to_date

bucket_name = 'corpor-sales-data'
df_sales_bucket = "gs://" + bucket_name + "/full_df/"
df_promo_bucket = "gs://" + bucket_name + "/df_promo_pivot/"
output_bucket = "gs://" + bucket_name + "/df_sales_long/"
store_bucket = "gs://" + bucket_name + "/stores.csv"
item_bucket = "gs://" + bucket_name + "/items.csv"

spark = SparkSession.builder.appName('store_item_merge').getOrCreate()
# credential_key_path = "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json"

# spark = SparkSession.builder \
#     .appName("GCS Example") \
#     .config("spark.driver.memory","4g") \
#     .config("spark.executor.memory","4g") \
#     .config("spark.jars", "file:///D:/utils/gcs-connector-hadoop3-latest.jar") \
#     .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
#     .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
#     .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
#     .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile",credential_key_path) \
#     .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df_sales = spark.read.parquet(df_sales_bucket)
df_promo_pivot = spark.read.parquet(df_promo_bucket)
columns = df_promo_pivot.columns
columns = [c for c in columns if c not in ['store_nbr','item_nbr']]
stack_expr = f"stack({len(columns)},"+",".join(f"'{c}',`{c}`" for c in columns)+") as (date,onpromotion)"
df_long = df_promo_pivot.select('store_nbr','item_nbr',expr(stack_expr))
df_long = df_long.withColumn('item_nbr',col('item_nbr').cast(IntegerType())) \
                 .withColumn('store_nbr',col('store_nbr').cast(ByteType())) \
                 .withColumn('onpromotion',col('onpromotion').cast(ByteType())) \
                 .withColumn('date',to_date(col('date'),'yyyy-MM-dd'))
df_long.write \
  .format('parquet') \
  .mode('overwrite') \
  .save("gs://" + bucket_name + "/df_promo_long/")

items = spark.read \
              .format('csv') \
              .option('header',True) \
              .option('inferschema',True) \
              .load(item_bucket)
stores = spark.read \
              .format('csv') \
              .option('header',True) \
              .option('inferschema',True) \
              .load(store_bucket)
df_sales = df_sales.join(items,
              on=['item_nbr'],
              how='left') \
        .join(stores,
              on=['store_nbr'],
              how='left')
        # .join(df_long,
        #       on=['store_nbr','item_nbr','date'],
        #       how='left')
df_sales = df_sales.withColumn('cluster',col('cluster').cast(ByteType())) \
        .withColumn('class',col('class').cast(ShortType())) \
        .withColumn('perishable',col('perishable').cast(ByteType())) \
        .withColumn('store_nbr',col('store_nbr').cast(ByteType())) \
        .withColumn('item_nbr',col('item_nbr').cast(IntegerType()))

df_sales.write \
  .format('parquet') \
  .mode('overwrite') \
  .save(output_bucket)
  
client = storage.Client()
bucket = client.bucket(bucket_name)
for blob_name in ['stores.csv','oil.csv','transactions.csv','holidays_events.csv']:
    blob = bucket.blob(blob_name)
    blob.delete()
blobs = bucket.list_blobs(prefix='full_df/')
for blob in blobs:
    blob.delete()


