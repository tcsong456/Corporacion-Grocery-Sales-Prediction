import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from math import log1p
from collections import Counter
from datetime import date, datetime
from data_preprocess.final_process import merge_full_data
from pyspark.sql.functions import col


def test_final_data(spark):
    sales_data = [
        ('2024-01-01', log1p(10), 1, 8),
        ('2024-01-02', log1p(15), 2, 12),
        ('2024-01-03', log1p(12), 3, 20)
        ]
    df_sales_long = spark.createDataFrame(sales_data, ['date', 'unit_sales', 'store_nbr', 'item_nbr'])

    promo_data = [
        (2, 10, 0, 1, 0, 0),
        (3, 20, 0, 0, 0, 0),
        (4, 15, 1, 1, 0, 1)
        ]
    df_promo_pivot = spark.createDataFrame(promo_data, ['store_nbr', 'item_nbr', '2024-01-01', '2024-01-02', '2024-01-03',
                                                        '2024-01-04'])
    items_data = [
        (8, 'CLEANING', 1044, 0),
        (12, 'GROCERY I', 2712, 1),
        (20, 'BREAD/BAKERY', 1032, 0),
        (30, 'AUTOMOTIVE', 6810, 0)
        ]
    df_items = spark.createDataFrame(items_data, ['item_nbr', 'family', 'class', 'perishable'])

    stores_data = [
        (1, 'Quito', 'Pichincha', 'D', 13),
        (2, 'Quito', 'Pichincha', 'C', 9),
        (3, 'Cayambe', 'Cotopaxi', 'A', 15),
        (4, 'Guayaquil', 'Guayas', 'C', 3)
        ]
    df_stores = spark.createDataFrame(stores_data, ['store_nbr', 'city', 'state', 'type', 'cluster'])

    df_sales, df_promo_long = merge_full_data(df_sales_long, df_promo_pivot, df_items, df_stores)

    expected_pivot_columns = Counter(['date', 'onpromotion', 'store_nbr', 'item_nbr'])
    assert Counter(df_promo_long.columns) == expected_pivot_columns

    expected_pivot_dtypes = dict(df_promo_long.dtypes)
    assert expected_pivot_dtypes['store_nbr'] == 'tinyint'
    assert expected_pivot_dtypes['item_nbr'] == 'int'
    assert expected_pivot_dtypes['onpromotion'] == 'tinyint'
    isinstance(expected_pivot_dtypes['date'], date)

    distinct_pivot_dates = [datetime.strptime(c, "%Y-%m-%d").date() for c in df_promo_pivot.columns if c not in ['store_nbr', 'item_nbr']]
    distinct_store_item = df_promo_pivot.select('store_nbr', 'item_nbr').distinct().collect()
    true_pivot_elements = [(r.date, r.store_nbr, r.item_nbr) for r in df_promo_long.select('store_nbr', 'item_nbr', 'date').collect()]
    expected_pivot_elements = [(d, c.store_nbr, c.item_nbr) for d in distinct_pivot_dates for c in distinct_store_item]
    assert Counter(true_pivot_elements) == Counter(expected_pivot_elements)

    pivot_null = df_promo_long.filter(col('onpromotion').isNull()).count()
    assert pivot_null == 0

    items_columns = [c for c in df_items.columns if c not in ['item_nbr']]
    stores_columns = [c for c in df_stores.columns if c not in ['store_nbr']]
    expected_columns = df_sales_long.columns + items_columns + stores_columns
    true_columns = df_sales.columns
    assert Counter(expected_columns) == Counter(true_columns)

    df_sales_dtypes = dict(df_sales.dtypes)
    assert df_sales_dtypes['cluster'] == 'tinyint'
    assert df_sales_dtypes['class'] == 'smallint'
    assert df_sales_dtypes['store_nbr'] == 'tinyint'
    assert df_sales_dtypes['item_nbr'] == 'int'
    assert df_sales_dtypes['perishable'] == 'tinyint'
    assert df_sales_dtypes['unit_sales'] == 'float'

    sales_null = df_sales.filter(col('unit_sales').isNull()).count()
    assert sales_null == 0

    df_sales_results = df_sales.orderBy(['store_nbr', 'item_nbr']).collect()
    assert df_sales_results[1]['family'] == 'GROCERY I'
    assert df_sales_results[1]['class'] == 2712
    assert df_sales_results[1]['perishable'] == 1
    assert df_sales_results[2]['city'] == 'Cayambe'
    assert df_sales_results[2]['state'] == 'Cotopaxi'
    assert df_sales_results[2]['type'] == 'A'
    assert df_sales_results[2]['cluster'] == 15

    for column in ['store_nbr', 'item_nbr']:
        expected_col = [row[column] for row in df_sales_long.select(column).collect()]
        true_col = [row[column] for row in df_sales.select(column).collect()]
        assert Counter(expected_col) == Counter(true_col)
    expected_dates = [datetime.strptime(c.date, "%Y-%m-%d").date() for c in df_sales_long.select('date').collect()]
    true_dates = [c.date for c in df_sales.select('date').collect()]
    assert Counter(expected_dates) == Counter(true_dates)

    df_sales_long = df_sales_long.sort(*df_sales_long.columns)
    df_sales = df_sales.sort(*df_sales.columns)
    expected_unit_sales = np.array([row['unit_sales'] for row in df_sales_long.select('unit_sales').collect()])
    true_unit_sales = np.array([row['unit_sales'] for row in df_sales.select('unit_sales').collect()])
    # assert all(isclose(a, b, rel_tol=1e-5, abs_tol=1e-8) for a, b in zip(expected_unit_sales, true_unit_sales))
    assert np.allclose(expected_unit_sales, true_unit_sales, rtol=1e-5, atol=1e-8)
