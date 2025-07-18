from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, log1p, to_date
from pyspark.sql.types import FloatType, IntegerType, ByteType


def transform_data(df, min_value=0, max_value=100):
    df = df.fillna({'unit_sales': 0})
    df = df.withColumn(
        'unit_sales',
        when(col('unit_sales') < min_value, min_value)
        .when(col('unit_sales') > max_value, max_value)
        .otherwise(col('unit_sales'))
        )

    df = df.withColumn(
        'unit_sales',
        log1p('unit_sales'))

    df = df.withColumn(
        'date',
        to_date(col('date'), 'yyyy-MM-dd')
        )

    df = df.withColumn(
        'unit_sales', col('unit_sales').cast(FloatType())
        ).withColumn(
            'item_nbr', col('item_nbr').cast(IntegerType())
            ).withColumn(
                'store_nbr', col('store_nbr').cast(ByteType())
                )
    return df


if __name__ == '__main__':
    bucket_name = "corpor-sales-data"
    train_bucket = "gs://" + bucket_name + "/train.csv"
    output_bucket = "gs://" + bucket_name + "/train/"

    spark = SparkSession.builder.appName('corpor_train_data_transformation').getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    train = spark.read.format("csv").option("header", True).option("inferschema", True).load(train_bucket)

    train = transform_data(train, min_value=0, max_value=1000)

    train.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(output_bucket)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob('train.csv')
    blob.delete()
