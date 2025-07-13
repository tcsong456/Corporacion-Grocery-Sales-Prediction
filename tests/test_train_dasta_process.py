import os
import sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import pytest
from math import isclose, log1p
from pyspark.sql.functions import col
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, ByteType
from .utils import upload_if_not_exists

@pytest.fixture(scope='session')
def spark():
    return SparkSession \
        .builder \
        .appName('unit-tests') \
        .master('local[*]') \
        .getOrCreate()


def test_transform_train_data(spark):
    input_data = [
        ('2024-05-01', -5.0, 10, 20),
        ('2024-05-02', 2000.0, 20, 30),
        ('2024-05-11', 50.0, 100, 200),
        ('2024-05-03', 300.0, 30, 40),
        ('2024-05-04', None, 40, 50)
        ]
    schema = StructType([
        StructField('date', StringType()),
        StructField('unit_sales', FloatType()),
        StructField('store_nbr', ByteType()),
        StructField('item_nbr', IntegerType())
        ])
    df = spark.createDataFrame(input_data, schema=schema)
    blob = upload_if_not_exists('data/train.csv')
    
    from data_preprocess.train_data_process import transform_data
    transformed_data = transform_data(df)
    data_list = transformed_data.collect()

    assert isclose(data_list[0]['unit_sales'], log1p(0.0), rel_tol=1e-5)
    assert isclose(data_list[1]['unit_sales'], log1p(1000.0), rel_tol=1e-5)
    assert isclose(data_list[2]['unit_sales'], log1p(50.0), rel_tol=1e-5)
    assert isclose(data_list[3]['unit_sales'], log1p(300.0), rel_tol=1e-5)
    assert transformed_data[0]['store_nbr'] == 10
    assert transformed_data[0]['item_nbr'] == 20
    assert transformed_data[-1]['store_nbr'] == 40
    assert transformed_data[-1]['item_nbr'] == 50

    null_count = transformed_data.filter(col('unit_sales').isNull()).count()
    assert null_count == 0, "Found null value for column 'unit_sales' after transformation"
    blob.delete()
