import os
import uuid
import time
from google.cloud import storage
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, ByteType


def create_bucket_and_upload_data(src_bucket_name, src_blob_name, dst_bucket_name, dst_blob_name):
    client = storage.Client()
    src_bucket = client.lookup_bucket(src_bucket_name)
    if src_bucket is None:
        raise FileNotFoundError(f'Bucket: {src_bucket_name} does not exist')
    else:
        if src_bucket.blob(src_blob_name).exists(client):
            src_blob = src_bucket.blob(src_blob_name)
        else:
            raise FileNotFoundError(f'blob: {src_blob_name} does not exist')

    dst_bucket = client.lookup_bucket(dst_bucket_name)
    if dst_bucket is not None:
        if dst_bucket.blob(dst_blob_name).exists(client):
            return
    else:
        location = os.environ['GCP_REGION']
        project = os.environ['GCP_PROJECT']
        dst_bucket = client.create_bucket(dst_bucket_name, location=location, project=project)
    src_bucket.copy_blob(src_blob, dst_bucket, dst_blob_name)


def compute_ordered_hash(df):
    df = df.orderBy(sorted(df.columns))
    return df.withColumn('row_hash', F.md5(F.concat_ws('-', *df.columns))) \
             .select('row_hash') \
             .agg(F.concat_ws('-' , F.collect_list('row_hash')).alias('all_hash')) \
             .select(F.md5(F.col('all_hash')).alias('final_hash')) \
             .collect()[0]['final_hash']


def test_gcs_read_write(spark):
    create_bucket_and_upload_data('corpor-sales-data', 'test.csv', 'integration_test_io', 'integration_test.csv')
    test_id = uuid.uuid4().hex[:8]
    input_path = "gs://integration_test_io/integration_test.csv"
    output_path = f"gs://integration_test_io/test_output_{test_id}.parquet"

    start_read_time = time.time()
    df_test = spark.read.option('header', 'true').csv(input_path)
    read_duration = time.time() - start_read_time
    assert read_duration < 20.0

    df_test = df_test.withColumn(
        'onpromotion',
        F.when(F.col('onpromotion') == 'True', 1)
        .when(F.col('onpromotion') == 'False', 0)
        .otherwise(F.col('onpromotion').cast('tinyint'))
        )

    df_promo_sum = df_test \
        .groupby('store_nbr', 'item_nbr') \
        .agg(F.sum('onpromotion').alias('promo_sum')) \
        .withColumn(
            'store_nbr', F.col('store_nbr').cast(ByteType())
            ) \
        .withColumn(
            'item_nbr', F.col('item_nbr').cast(IntegerType())
            ) \
        .withColumn(
            'promo_sum', F.col('promo_sum').cast(IntegerType())
            )

    df_test_schema = StructType([
        StructField('store_nbr', ByteType()),
        StructField('item_nbr', IntegerType()),
        StructField('promo_sum', IntegerType())
        ])

    start_write_time = time.time()
    df_promo_sum \
        .coalesce(1) \
        .write \
        .mode('overwrite') \
        .parquet(output_path)
    write_duration = time.time() - start_write_time
    assert write_duration < 30.0

    df_promo_test = spark.read.parquet(output_path)
    assert df_promo_test.schema == df_test_schema

    df1_hash = compute_ordered_hash(df_promo_test)
    df2_hash = compute_ordered_hash(df_promo_sum)

    assert df1_hash == df2_hash
