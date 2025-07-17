import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, ByteType, LongType, DoubleType
from data_preprocess.promo_nan_fill import promo_fill


np.random.seed(398)


def test_promo_basics(spark):
    data = [
        ('2024-01-01', 1, 1, 10),
        ('2024-01-03', 0, 2, 10),
        ('2024-01-10', 0, 3, 12),
        ('2024-01-11', None, 1, 10),
        ('2024-01-12', 1, 2, 20),
        ('2024-01-15', None, 4, 15)
        ]
    schema = StructType([
        StructField('date', StringType()),
        StructField('onpromotion', IntegerType()),
        StructField('store_nbr', ByteType()),
        StructField('item_nbr', IntegerType())
        ])

    df = spark.createDataFrame(data, schema=schema)
    df_long, df_pivot = promo_fill(df)

    assert set(df_long.columns) == {'date', 'onpromotion', 'store_nbr', 'item_nbr'}
    dates = df.select('date').distinct().collect()
    store_item = df.select('store_nbr', 'item_nbr').distinct().collect()
    expected_pivot_columns = ['store_nbr', 'item_nbr'] + [d['date'] for d in dates]
    assert set(expected_pivot_columns) == set(df_pivot.columns)
    expected_pivot_index = [(c.store_nbr, c.item_nbr) for c in store_item]
    true_pivot_index = [(c.store_nbr, c.item_nbr) for c in df_pivot.select('store_nbr', 'item_nbr').collect()]
    assert set(expected_pivot_index) == set(true_pivot_index)

    expected_long_index = [(r.date, c.store_nbr, c.item_nbr) for r in dates for c in store_item]
    true_long_index = [(c.date, c.store_nbr, c.item_nbr) for c in df_long.select('date', 'store_nbr', 'item_nbr').collect()]
    assert set(expected_long_index) == set(true_long_index)

    promo_null_count = df_long.filter(df_long['onpromotion'].isNull()).count()
    assert promo_null_count == 0
    distinct_promo = [r[0] for r in df_long.select('onpromotion').distinct().collect()]
    assert all(v in [0, 1] for v in distinct_promo)


def test_logic_of_promo_fill(spark):
    rand = np.random.rand(500)
    rand_values = np.where(
        rand < 0.35, None,
        np.where(rand < 0.75, 0.0, 1.0)
        )
    data = {
        'row_id': np.arange(500),
        '2024-01-01': rand_values}

    schema = StructType([
        StructField('row_id', LongType(), False),
        StructField('2024-01-01', DoubleType(), True)
        ])
    df = spark.createDataFrame(pd.DataFrame(data), schema)
    mean = df.select(F.mean(F.col('2024-01-01'))).collect()[0][0]
    mean_dict = {'2024-01-01': mean if mean is not None else 0}
    columns = ['2024-01-01']

    def process_batch(pdf_iter):
        for pdf in pdf_iter:
            for c in columns:
                p = 0.2 * mean_dict.get(c, 0.0)
                mask = pdf[c].isna()
                pdf.loc[mask, c] = np.random.binomial(n=1, p=p, size=mask.sum()).astype(np.int64)
            yield pdf[['row_id'] + columns]

    schema = StructType([
        StructField('row_id', LongType()),
        StructField('2024-01-01', LongType())
        ])
    df_filled = df.mapInPandas(process_batch, schema=schema)
    df_pd = df_filled.toPandas()

    assert df_pd['2024-01-01'].isna().sum() == 0
    assert set(df_pd['2024-01-01']).issubset({0, 1})
    null_indices = pd.isna(rand_values)
    value_for_none = df_pd.loc[null_indices, '2024-01-01']
    mean_value = value_for_none.mean()
    expected_mean = 0.2 * mean
    std_dev = 3 * np.sqrt(expected_mean * (1 - expected_mean) / value_for_none.shape[0])
    assert abs(mean_value - expected_mean) <= std_dev
