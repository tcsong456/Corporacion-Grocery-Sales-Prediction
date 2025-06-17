# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 18:22:12 2025

@author: congx
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import when,col
from pyspark.sql.types import ByteType
# from google.cloud import storage

bucket_name = "corpor-sales-data"
df_bucket = "gs://" + bucket_name + "/df/"
output_bucket = "gs://" + bucket_name + "/full_df/"
# credential_key_path = "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json"

spark = SparkSession.builder.appName('missing_value_fill').getOrCreate()
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

store_item_df = df.select('store_nbr','item_nbr').distinct()
date_df = df.select('date').distinct()
full_df = store_item_df.crossJoin(date_df)
df = full_df.join(df.select('store_nbr','item_nbr','date','unit_sales','onpromotion'),
                  on=['store_nbr','item_nbr','date'],
                  how='left')
df = df.withColumn('onpromotion',
                   when(col('onpromotion').isNull(),2)
                   .otherwise(col('onpromotion').cast('int'))
                   .cast(ByteType())
                   )
df = df.withColumn('unit_sales',
                   when(col('unit_sales').isNull(),0)
                   .otherwise(col('unit_sales').cast('float'))
                   )
    
df.write \
    .format('parquet') \
    .mode('overwrite') \
    .save(output_bucket)

# client = storage.Client()
# bucket = client.bucket(bucket_name)
# blobs = list(bucket.list_blobs(prefix='df/'))
# for blob in blobs:
#     blob.delete()