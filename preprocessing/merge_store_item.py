# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 16:42:56 2025

@author: congx
"""
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.types import ByteType,ShortType
from pyspark.sql.functions import col

bucket_name = 'corpor-sales-data'
df_bucket = "gs://" + bucket_name + "/full_df/"
output_bucket = "gs://" + bucket_name + "/df_sales_corpor/"
store_bucket = "gs://" + bucket_name + "/stores.csv"
item_bucket = "gs://" + bucket_name + "/items.csv"
# credential_key_path = "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json"

spark = SparkSession.builder.appName('store_item_merge').getOrCreate()
# spark = SparkSession.builder \
#     .appName("corpor_train_test_concat") \
#     .config("spark.driver.memory","8g") \
#     .config("spark.executor.memory","8g") \
#     .config("spark.jars", "file:///D:/utils/gcs-connector-hadoop3-latest.jar") \
#     .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
#     .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
#     .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
#     .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile",credential_key_path) \
#     .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df = spark.read.parquet(df_bucket)
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
df = df.join(items,
             on=['item_nbr'],
             how='left') \
       .join(stores,
             on=['store_nbr'],
             how='left')
df = df.withColumn('cluster',col('cluster').cast(ByteType())) \
       .withColumn('class',col('class').cast(ShortType())) \
       .withColumn('perishable',col('perishable').cast(ByteType()))
df.write \
  .format('parquet') \
  .mode('overwrite') \
  .save(output_bucket)
  
# client = storage()
# bucket = client.bucket(bucket_name)
# for blob_name in ['items.csv','stores.csv']:
#     blob = bucket.blob(blob_name)
#     blob.delete()
# blobs = list(bucket.list_blobs(prefix='full_df/'))
# for blob in blobs:
#     blob.delete()


