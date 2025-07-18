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
