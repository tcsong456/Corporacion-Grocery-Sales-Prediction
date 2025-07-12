# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:19:02 2025

@author: congx
"""
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, log1p, to_date
from pyspark.sql.types import FloatType, IntegerType, ByteType

bucket_name = "corpor-sales-data"
train_bucket = "gs://" + bucket_name + "/train.csv"
output_bucket = "gs://" + bucket_name + "/train/"

spark = SparkSession.builder.appName('corpor_train_data_transformation').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
train = spark.read.format("csv").option("header", True).option("inferschema", True).load(train_bucket)
min_value = 0
max_value = 1000
train = train.withColumn('unit_sales',
                         when(col('unit_sales') < min_value, min_value)
                         .when(col('unit_sales') > max_value, max_value)
                         .otherwise(col('unit_sales')))
train = train.withColumn('unit_sales',
                         log1p('unit_sales'))
train = train.withColumn('date', to_date(col('date'), 'yyyy-MM-dd'))
train = train.withColumn('unit_sales', col('unit_sales').cast(FloatType())) \
             .withColumn('item_nbr', col('item_nbr').cast(IntegerType())) \
             .withColumn('store_nbr', col('store_nbr').cast(ByteType()))
train.write \
    .format("parquet") \
    .mode("overwrite") \
    .save(output_bucket)

client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob('train.csv')
blob.delete()
