const datasets = ['store_item_has_promo_first_last_app',
                  'item_has_promo_first_last_app',
                  'class_store_has_promo_first_last_app',
                  'store_item_no_promo_first_last_app',
                  'item_no_promo_first_last_app',
                  'class_store_no_promo_first_last_app',
                  'store_item_future_promo_indicators',
                  'item_future_promo_indicators',
                  'class_store_future_promo_indicators',
                  'store_item_has_promo_sales_decay_sum',
                  'item_has_promo_sales_decay_sum',
                  'class_store_has_promo_sales_decay_sum',
                  'store_item_no_promo_sales_decay_sum',
                  'item_no_promo_sales_decay_sum',
                  'class_store_no_promo_sales_decay_sum',
                  'store_item_has_promo_sales_sum',
                  'item_has_promo_sales_sum',
                  'class_store_has_promo_sales_sum',
                  'store_item_no_promo_sales_sum',
                  'item_no_promo_sales_sum',
                  'class_store_no_promo_sales_sum',
                  'store_item_promo_sum',
                  'item_promo_sum',
                  'class_store_promo_sum',
                  'store_item_rolling_sales_stats',
                  'item_rolling_sales_stats',
                  'class_store_rolling_sales_stats',
                  'store_item_dow_mean',
                  'item_dow_mean',
                  'class_store_dow_mean'];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];



/*
SELECT
  t0.*,
  t1.*,
  t2.*,
  t3.*
  FROM t0 
  LEFT JOIN t1 on t0.a = t1.a AND t0.b = t1.b
  LEFT JOIN t2 on t0.a = t2.a AND t0.b = t2.b
  LEFT JOIN t3 on t0.a = t3.a AND t0.b = t3.b
  LEFT JOIN t4 on t0.a = t4.a AND t0.b = t4.b
  */