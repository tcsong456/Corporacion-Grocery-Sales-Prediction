# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 20:37:16 2025

@author: congx
"""
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,to_date
from pyspark.sql.types import ByteType

bucket_name = "corpor-sales-data"
train_bucket  = "gs://" + bucket_name + "/train/"
test_bucket = "gs://" + bucket_name + "/test.csv"
output_path = "gs://" + bucket_name + "/df/"

spark = SparkSession.builder.appName('corpor_train_test_concat').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

train = spark.read.parquet(train_bucket)
test = spark.read.format("csv").option("header",True).option("inferSchema",True).load(test_bucket)
test = test.withColumn('date',to_date(col('date'),'yyyy-MM-dd'))
test = test.withColumn('store_nbr',col('store_nbr').cast(ByteType()))

df = train.unionByName(test,allowMissingColumns=True)

df.write \
  .format("parquet") \
  .mode("overwrite") \
  .save(output_path)

client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob('test.csv')
blob.delete()
blobs = list(bucket.list_blobs(prefix='train/'))
for blob in blobs:
    blob.delete()
