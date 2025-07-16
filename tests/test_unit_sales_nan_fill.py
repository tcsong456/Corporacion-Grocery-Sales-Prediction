import os
import sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from math import log1p
from data_preprocess.unit_sales_nan_fill import build_whole_dataset
from pyspark.sql import functions as F

def test_long_pivot_dataset(spark):
    data = [
        ('2024-01-01',1,10,log1p(10)),
        ('2024-01-02',2,15,log1p(20)),
        ('2024-01-01',4,25,log1p(15)),
        ('2024-01-02',3,20,None)
        ]
    df = spark.createDataFrame(data, ['date','store_nbr','item_nbr','unit_sales'])
    df = df.withColumn('date', F.to_date(F.col('date'),'yyyy-MM-dd'))
    df_long, df_pivot = build_whole_dataset(df)
    results_long = df_long.collect()
    
    assert len(results_long) == 8
    data_types = df_long.dtypes
    assert dict(data_types)['store_nbr'] == 'tinyint'
    assert dict(data_types)['item_nbr'] == 'int'
    null_count = df_long.filter(F.col('unit_sales').isNull()).count()
    assert null_count == 0
    
    expected_dates = df_long.select('date').distinct().collect()
    expected_combs = df_long.select('store_nbr','item_nbr').distinct().collect()
    expected_index = set([(c.store_nbr,c.item_nbr,d.date) for d in expected_dates for c in expected_combs])
    true_index = set([(r.store_nbr,r.item_nbr,r.date) for r in df_long.select('store_nbr','item_nbr','date').collect()])
    assert expected_index == true_index
    
    dates = [row['date'].strftime("%Y-%m-%d") for row in df.select('date').distinct().collect()]
    expected_columns = set(['store_nbr','item_nbr'] + dates)
    expected_index = set([(r.store_nbr,r.item_nbr) for r in df.select('store_nbr','item_nbr').distinct().collect()])
    true_index = set([(r.store_nbr,r.item_nbr) for r in df_pivot.select('store_nbr','item_nbr').collect()])
    assert expected_columns == set(df_pivot.columns)
    assert expected_index == true_index
    
    null_count = df_pivot.select([F.col(c).isNull().cast('int').alias(c) for c in df_pivot.columns]).agg(
            *[F.sum(F.col(c)).alias(c) for c in df_pivot.columns]
            ).collect()[0].asDict()
    assert all(v==0 for v in null_count.values())