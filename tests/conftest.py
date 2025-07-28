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
    spark = SparkSession \
        .builder \
        .appName('integration_test') \
        .config("spark.jars", "/opt/jars/gcs-connector.jar") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.type", "APPLICATION_DEFAULT") \
        .master('local[*]') \
        .getOrCreate()
    print("fs.gs.impl:", spark._jsc.hadoopConfiguration().get("fs.gs.impl"))
    jars = spark._jvm.scala.collection.JavaConversions.asJavaCollection(
        spark.sparkContext._jsc.sc().listJars())
    print("GCS connector found:", any("gcs-connector" in str(jar) for jar in jars))
    yield spark
    spark.stop()
