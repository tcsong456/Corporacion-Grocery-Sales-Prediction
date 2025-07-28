import os
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope='session')
def spark():
    spark = SparkSession \
        .builder \
        .appName('unit-tests') \
        .master('local[*]') \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()


@pytest.fixture(scope='session')
def gcs_spark():
    spark_ = SparkSession.builder.getOrCreate()
    hadoop_ver = spark_._jvm.org.apache.hadoop.util.VersionInfo.getVersion()
    print("Hadoop:", hadoop_ver)
    print(os.path.exists("/opt/jars/gcs-connector.jar")) 
    spark = SparkSession \
        .builder \
        .appName('integration_test') \
        .config("spark.jars", "/opt/jars/gcs-connector.jar") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.type", "APPLICATION_DEFAULT") \
        .master('local[*]') \
        .getOrCreate()
    yield spark
    spark.stop()
