import os
import sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import pytest
from math import isclose, log1p
from pyspark.sql.functions import col
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, ByteType
from data_preprocess.train_data_process import transform_data


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


def test_transform_train_data(spark):
    input_data = [
        ('2024-05-01', -5.0, 1, 20),
        ('2024-05-02', 2000.0, 2, 30),
        ('2024-05-11', 50.0, 10, 200),
        ('2024-05-03', 300.0, 3, 40),
        ('2024-05-04', None, 4, 50)
        ]
    schema = StructType([
        StructField('date', StringType()),
        StructField('unit_sales', FloatType()),
        StructField('store_nbr', ByteType()),
        StructField('item_nbr', IntegerType())
        ])
    df = spark.createDataFrame(input_data, schema=schema)
    
    transformed_data = transform_data(df,0,1000)
    data_list = transformed_data.collect()

    assert isclose(data_list[0]['unit_sales'], log1p(0.0), rel_tol=1e-5)
    assert isclose(data_list[1]['unit_sales'], log1p(1000.0), rel_tol=1e-5)
    assert isclose(data_list[2]['unit_sales'], log1p(50.0), rel_tol=1e-5)
    assert isclose(data_list[3]['unit_sales'], log1p(300.0), rel_tol=1e-5)
    assert data_list[0]['store_nbr'] == 1
    assert data_list[0]['item_nbr'] == 20
    assert data_list[-1]['store_nbr'] == 4
    assert data_list[-1]['item_nbr'] == 50

    null_count = transformed_data.filter(col('unit_sales').isNull()).count()
    assert null_count == 0, "Found null value for column 'unit_sales' after transformation"
