# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 16:29:50 2025

@author: congx
"""
from google.cloud import storage
from google.oauth2 import service_account
from pyspark.sql import SparkSession
from pyspark.sql.functions import log1p

bucket_name = "corpor-sales-data"
train_bucket = "gs://" + bucket_name + "/pivot/"
credential_key_path = "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json"
# spark = SparkSession.builder.appName('corpor_data_processing').getOrCreate()
spark = SparkSession.builder \
    .appName("GCS Example") \
    .config("spark.driver.memory","4g") \
    .config("spark.executor.memory","4g") \
    .config("spark.jars", "file:///D:/utils/gcs-connector-hadoop3-latest.jar") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile",credential_key_path) \
    .getOrCreate()

# items = spark.read.format("csv").option("header",True).option("inferschema",True).load(item_bucket)
# items = items.withColumn('item_nbr',
#                          log1p('item_nbr'))
# items.coalesce(1).write \
#       .format("csv") \
#       .option("header", True) \
#       .mode("overwrite") \
#       .save("gs://corpor-sales-data/items/")

# client = storage.Client()
# bucket = client.bucket(bucket_name)
# blobs = list(bucket.list_blobs(prefix='items/'))
# for blob in blobs:
#     if 'part' in blob.name and blob.name.endswith('.csv'):
#         new_blob = bucket.copy_blob(blob,bucket,'items.csv')
#     blob.delete()

from pyspark.sql.functions import sequence, to_date, lit, explode,col
from pyspark.sql.types import DateType

# Define min and max dates
min_date = "2013-01-01"
max_date = "2017-08-15"

store_item_df
#%%
# df = df.withColumn('onpromotion',
#                    when(col('onpromotion').isNull(),2)
#                    .otherwise(col('onpromotion').cast('int'))
#                    .cast(ByteType())
#                    )
# date_bounds = df.select(spark_min('date').alias('min_date'),spark_max('date').alias('max_date')).first()
# min_date,max_date = date_bounds['min_date'],date_bounds['max_date']
# min_date = datetime.combine(min_date,datetime.min.time())
# max_date = datetime.combine(max_date,datetime.min.time())
# dates_list = [(min_date+timedelta(days=d),) for d in range((max_date-min_date).days+1)]
# dates_df = spark.createDataFrame(dates_list,['date'])
# dates_df = df.select('date').distinct()
# dates_df.show(20)
# store_item_df = df.select('store_nbr','item_nbr').distinct()
# full_index_df = store_item_df.crossJoin(dates_df)
# full_index_df.show(20)

