from math import log1p, isclose
from datetime import date
from pyspark.sql.functions import to_date, col
from pyspark.sql.types import StructField, StructType, StringType, ByteType, FloatType, IntegerType


def test_concat_train_test_data(spark):
    train_data = [
        ('2024-01-01', log1p(25.0), 1, 10),
        ('2024-02-10', log1p(0), 2, 20)
        ]

    schema = StructType([
        StructField('date', StringType()),
        StructField('unit_sales', FloatType()),
        StructField('store_nbr', ByteType()),
        StructField('item_nbr', IntegerType())
        ])

    train = spark.createDataFrame(train_data, schema=schema)
    train = train.withColumn(
        'date',
        to_date(col('date'), 'yyyy-MM-dd')
        )

    test_data = [
        ('2024-05-22', 3, 30),
        ('2024-05-23', 4, 40)
        ]
    schema = StructType([
        StructField('date', StringType()),
        StructField('store_nbr', ByteType()),
        StructField('item_nbr', IntegerType())
        ])
    test = spark.createDataFrame(test_data, schema=schema)
    test = test.withColumn(
        'date',
        to_date(col('date'), 'yyyy-MM-dd')
        )

    df = train.unionByName(test, allowMissingColumns=True)
    results = df.collect()

    assert df.columns == ['date', 'unit_sales', 'store_nbr', 'item_nbr']
    assert len(results) == 4
    assert results[2]['unit_sales'] is None
    data_types = df.dtypes
    assert dict(data_types)['unit_sales'] == 'float'
    assert dict(data_types)['item_nbr'] == 'int'
    assert dict(data_types)['store_nbr'] == 'tinyint'
    assert isinstance(results[0]['date'], date)
    assert isclose(results[0]['unit_sales'], log1p(25.0), rel_tol=1e-5)
    assert results[1]['unit_sales'] == 0
    assert results[2]['store_nbr'] == 3
    assert results[3]['item_nbr'] == 40
