# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 18:22:12 2025

@author: congx
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, first
from pyspark.sql.types import ByteType, IntegerType

bucket_name = "corpor-sales-data"
df_bucket = "gs://" + bucket_name + "/df/"
output_bucket = "gs://" + bucket_name + "/full_df/"
pivot_output_bucket = "gs://" + bucket_name + "/df_sales_pivot/"

spark = SparkSession.builder.appName('missing_value_fill').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df = spark.read.parquet(df_bucket)

store_item_df = df.select('store_nbr', 'item_nbr').distinct()
date_df = df.select('date').distinct()
full_df = store_item_df.crossJoin(date_df)
df = full_df.join(df.select('store_nbr', 'item_nbr', 'date', 'unit_sales'),
                  on=['store_nbr', 'item_nbr', 'date'],
                  how='left')
df = df.withColumn('unit_sales',
                   when(col('unit_sales').isNull(), 0)
                   .otherwise(col('unit_sales').cast('float'))
                   )
df = df.withColumn('item_nbr', col('item_nbr').cast(IntegerType())) \
       .withColumn('store_nbr', col('store_nbr').cast(ByteType()))
df_sales_pivot = df.groupby('store_nbr', 'item_nbr') \
                   .pivot('date') \
                   .agg(first('unit_sales'))
df_sales_pivot = df_sales_pivot.fillna(0)

df.write \
    .format('parquet') \
    .mode('overwrite') \
    .save(output_bucket)

df_sales_pivot.write \
    .format('parquet') \
    .mode('overwrite') \
    .save(pivot_output_bucket)
