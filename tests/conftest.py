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
    spark = (
        SparkSession.builder
        .appName("integration_test")
        .master("local[*]")
        .config("spark.jars", "/opt/jars/gcs-connector.jar")
        .config("spark.driver.extraClassPath", "/opt/jars/gcs-connector.jar")
        .config("spark.executor.extraClassPath", "/opt/jars/gcs-connector.jar")
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
        .config("spark.hadoop.google.cloud.auth.type", "APPLICATION_DEFAULT")
        .config("spark.hadoop.fs.gs.project.id", os.getenv("GCP_PROJECT", "corporacion-sales-prediction"))
        .getOrCreate()
        )
    yield spark
    spark.stop()
