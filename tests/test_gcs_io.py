# import os
import uuid
import time
from google.cloud import storage
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, ByteType

# key_path = os.path.join(os.path.dirname(__file__), '..', 'key.json')
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path


def create_bucket_and_upload_data(bucket_name, blob_name, data_path):
    client = storage.Client()
    existing_bucket = client.lookup_bucket(bucket_name)
    if existing_bucket is not None:
        return

    client.create_bucket(bucket_name, location='europe-west1', project='corporacion-sales-prediction')
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(data_path)


def compute_ordered_hash(df):
    df = df.orderBy(sorted(df.columns))
    return df.withColumn('row_hash', F.md5(F.concat_ws('-', *df.columns))) \
             .select('row_hash') \
             .agg(F.concat_ws('-' , F.collect_list('row_hash')).alias('all_hash')) \
             .select(F.md5(F.col('all_hash')).alias('final_hash')) \
             .collect()[0]['final_hash']


def test_gcs_read_write(spark):
    # import os
    # import logging
    # log = logging.getLogger(__name__)
    # hadoop_ver = gcs_spark._jvm.org.apache.hadoop.util.VersionInfo.getVersion()
    # log.info("Hadoop: %s", hadoop_ver)
    # log.info("GCS connector present: %s", os.path.exists("/opt/jars/gcs-connector.jar"))
    # log.info("GCS connector present on disk: %s", os.path.exists("/opt/jars/gcs-connector-hadoop3-2.2.17.jar"))
    # try:
    #     spark._jvm.java.lang.Class.forName(
    #         "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
    #     )
    #     log.info("GCS connector class is on the classpath")
    # except Exception as e:
    #     log.info(f"GCS connector class NOT found:{e}")
    # log.info("spark.jars =", spark.sparkContext.getConf().get("spark.jars", ""))
    # hc = spark._jsc.hadoopConfiguration()
    # log.info("fs.gs.impl =", hc.get("fs.gs.impl"))
    # log.info("fs.AbstractFileSystem.gs.impl =", hc.get("fs.AbstractFileSystem.gs.impl"))

    create_bucket_and_upload_data('integration_test_io', 'integration_test.csv', 'data/test.csv')
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
