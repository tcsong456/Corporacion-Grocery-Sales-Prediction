# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 20:37:16 2025

@author: congx
"""
# from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,to_date
from pyspark.sql.types import ByteType
# from google.oauth2 import service_account

bucket_name = "corpor-sales-data"
train_bucket  = "gs://" + bucket_name + "/train/"
test_bucket = "gs://" + bucket_name + "/test.csv"
# credential_key_path = "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json"
output_path = "gs://" + bucket_name + "/df/"

spark = SparkSession.builder.appName('corpor_train_test_concat').getOrCreate()
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

train = spark.read.parquet(train_bucket)
test = spark.read.format("csv").option("header",True).option("inferSchema",True).load(test_bucket)
test = test.withColumn('date',to_date(col('date'),'yyyy-MM-dd'))
test = test.withColumn('store_nbr',col('store_nbr').cast(ByteType()))

df = train.unionByName(test,allowMissingColumns=True)

df.write \
  .format("parquet") \
  .mode("overwrite") \
  .save(output_path)
  
# credentials = service_account.Credentials.from_service_account_file(credential_key_path)
# client = storage.Client(credentials=credentials)

# client = storage.Client()
# bucket = client.bucket(bucket_name)
# blob = bucket.blob('test.csv')
# blob.delete()
# blobs = list(bucket.list_blobs(prefix='train/'))
# for blob in blobs:
#     blob.delete()
