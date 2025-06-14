# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:19:02 2025

@author: congx
"""
from google.cloud import storage
# from google.oauth2 import service_account
from pyspark.sql import SparkSession
from pyspark.sql.functions import when,col,log1p,to_date
from pyspark.sql.types import FloatType,IntegerType,ByteType

bucket_name = "corpor-sales-data"
train_bucket = "gs://" + bucket_name + "/train.csv"
# credential_key_path = "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json"

spark = SparkSession.builder.appName('corpor_data_processing').getOrCreate()
# 
# spark = SparkSession.builder \
#     .appName("GCS Example") \
#     .config("spark.jars", "file:///D:/utils/gcs-connector-hadoop3-latest.jar") \
#     .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
#     .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
#     .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
#     .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile",credential_key_path) \
#     .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
train = spark.read.format("csv").option("header",True).option("inferschema",True).load(train_bucket)
min_value = 0
max_value = 1000
train = train.withColumn('unit_sales',
                         when(col('unit_sales')<min_value,min_value)
                         .when(col('unit_sales')>max_value,max_value)
                         .otherwise(col('unit_sales')))
train = train.withColumn('unit_sales',
                         log1p('unit_sales'))
train = train.withColumn('date',to_date(col('date'),'yyyy-MM-dd'))
train = train.withColumn('unit_sales',col('unit_sales').cast(FloatType())) \
             .withColumn('item_nbr',col('item_nbr').cast(IntegerType())) \
             .withColumn('store_nbr',col('store_nbr').cast(ByteType()))
train.coalesce(1).write \
      .format("csv") \
      .option("header", True) \
      .mode("overwrite") \
      .save("gs://corpor-sales-data/train/")

# credentials = service_account.Credentials.from_service_account_file(credential_key_path)
# client = storage.Client(credentials=credentials)
client = storage.Client()
bucket = client.bucket(bucket_name)
blobs = list(bucket.list_blobs(prefix='train/'))
for blob in blobs:
    if 'part' in blob.name and blob.name.endswith('.csv'):
        new_blob = bucket.copy_blob(blob,bucket,'train.csv')
    blob.delete()


#%%
