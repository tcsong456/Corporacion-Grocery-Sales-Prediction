# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 19:46:02 2025

@author: congx
"""
import numpy as np
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import first, col, expr, row_number
from pyspark.sql.types import ByteType, StructField, StructType, IntegerType
from pyspark.sql.window import Window
from pyspark.sql import functions as F

bucket_name = 'corpor-sales-data'
df_bucket = "gs://" + bucket_name + "/df/"
df_output_bucket = "gs://" + bucket_name + "/df_promo_long/"
df_pivot_output_bucket = "gs://" + bucket_name + "/df_promo_pivot/"

spark = SparkSession.builder.appName('promo_nan_fill').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df = spark.read.parquet(df_bucket)
df = df.withColumn(
    'onpromotion',
    col('onpromotion').cast(ByteType()))
all_store_item = df.select('store_nbr', 'item_nbr').distinct()

df_pivot = df.groupby(
    'store_nbr', 'item_nbr') \
    .pivot('date') \
    .agg(first('onpromotion').cast('integer'))
df_pivot = all_store_item.join(df_pivot, on=['store_nbr', 'item_nbr'], how='left')

columns = df_pivot.columns
columns = [c for c in columns if c not in ['store_nbr', 'item_nbr']]
mean_rows = df_pivot.select([F.mean(col(c)).alias(c) for c in columns]).first()
mean_rows_dict = {c: (mean_rows[c] if mean_rows[c] is not None else 0) for c in columns}

window = Window.orderBy('store_nbr', 'item_nbr')
df_pivot = df_pivot.withColumn('row_id', row_number().over(window))
df_promo = df_pivot.select(['row_id'] + columns).orderBy('row_id')
output_schema = StructType(
    [StructField('row_id', IntegerType())]
    + [StructField(c, IntegerType()) for c in columns]
    )


def process_batch(pdf_iter):
    for pdf in pdf_iter:
        for c in columns:
            p = 0.2 * mean_rows_dict.get(c, 0.0)
            mask = pdf[c].isna()
            pdf.loc[mask, c] = np.random.binomial(n=1, p=p, size=mask.sum()).astype(np.int64)
        yield pdf[['row_id'] + columns]


df_promo = df_promo.mapInPandas(process_batch, schema=output_schema)
df_pivot = df_pivot.select(['store_nbr', 'item_nbr', 'row_id']).join(df_promo, on='row_id', how='left').drop('row_id')

stack_expr = f"stack({len(columns)}," + ",".join(f"'{c}',`{c}`" for c in columns) + ") as (date,onpromotion)"
df_long = df_pivot.select('store_nbr', 'item_nbr', expr(stack_expr))
df_long = df_long.withColumn('item_nbr', col('item_nbr').cast(IntegerType())) \
                 .withColumn('store_nbr', col('store_nbr').cast(ByteType()))

df_pivot.write \
    .format('parquet') \
    .mode('overwrite') \
    .save(df_pivot_output_bucket)

df_long.write \
    .format('parquet') \
    .mode('overwrite') \
    .save(df_output_bucket)

client = storage.Client()
bucket = client.bucket(bucket_name)
blobs = bucket.list_blobs(prefix='df/')
for blob in blobs:
    blob.delete()
