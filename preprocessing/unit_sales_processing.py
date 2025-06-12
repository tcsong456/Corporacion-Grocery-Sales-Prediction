# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:19:02 2025

@author: congx
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import when,col

bucket_name = "corpor-sales-bucket"
train = "gs://" + bucket_name + "/train.csv"

# spark = SparkSession.builder.appName('corpor_data_processing').getOrCreate()
# 
spark = SparkSession.builder \
    .appName("GCS Example") \
    .config("spark.jars", "file:///D:/utils/gcs-connector-hadoop3-latest.jar") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "D:/machine_learning/projects/Corporacion-Grocery-Sales-Prediction/key.json") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
train = spark.read.format("csv").option("header",True).option("inferschema",True).load(train)
min_value = 0
max_value = 1000
train = train.withColumn()

#%%