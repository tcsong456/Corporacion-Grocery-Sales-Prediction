publish('store_item_class_mock_2017614', { type: "table", tags: ["unit_test"] }).query(ctx => `
  SELECT * FROM UNNEST([
    STRUCT(1 AS store_nbr, 10 AS item_nbr, 1000 AS class),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, 2000 AS class),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, 1000 AS class),
    STRUCT(4 AS store_nbr, 40 AS item_nbr, 2000 AS class)
  ])
`);

publish("store_item_rolling_stats_mock_2017614", { type: "table", tags: ["unit_test"] }).query(ctx => `
  SELECT * FROM UNNEST([
    STRUCT(1 AS store_nbr, 10 AS item_nbr, 0 AS store_item_unit_sales_min_7, 11 AS store_item_unit_sales_max_7,
           6.5 AS store_item_unit_sales_mean_7, 5.2 AS store_item_unit_sales_median_7, 2.345 AS store_item_unit_sales_std_7,
           18.732 AS store_item_unit_sales_decay_sum_7),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, 0 AS store_item_unit_sales_min_7, 9 AS store_item_unit_sales_max_7,
           5.5 AS store_item_unit_sales_mean_7, 4.76 AS store_item_unit_sales_median_7, 1.987 AS store_item_unit_sales_std_7,
           13.3 AS store_item_unit_sales_decay_sum_7),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, 0.5 AS store_item_unit_sales_min_7, 21 AS store_item_unit_sales_max_7,
           10.12 AS store_item_unit_sales_mean_7, 9.598 AS store_item_unit_sales_median_7, 2.954 AS store_item_unit_sales_std_7,
           30.285 AS store_item_unit_sales_decay_sum_7),
    STRUCT(4 AS store_nbr, 40 AS item_nbr, 0 AS store_item_unit_sales_min_7, 8 AS store_item_unit_sales_max_7,
           6 AS store_item_unit_sales_mean_7, 4.5 AS store_item_unit_sales_median_7, 1.15 AS store_item_unit_sales_std_7,
           12.3467 AS store_item_unit_sales_decay_sum_7)
  ])
`);

publish("item_promo_first_last_app_mock_2017614", { type: "table", tags: ["unit_test"] }).query(ctx => `
  SELECT * FROM UNNEST([
    STRUCT(10 AS item_nbr, 1 AS item_last_sales_app_past_14_days, 13 AS item_first_sales_app_past_14_days,
           42 AS item_has_sales_in_last_14_days, 3 AS item_percent_days_with_sales_last_14_days),
    STRUCT(20 AS item_nbr, 0 AS item_last_sales_app_past_14_days, 10 AS item_first_sales_app_past_14_days,
           25 AS item_has_sales_in_last_14_days, 1.785 AS item_percent_days_with_sales_last_14_days),
    STRUCT(30 AS item_nbr, 3 AS item_last_sales_app_past_14_days, 13 AS item_first_sales_app_past_14_days,
           14 AS item_has_sales_in_last_14_days, 4 AS item_percent_days_with_sales_last_14_days),
    STRUCT(40 AS item_nbr, 2 AS item_last_sales_app_past_14_days, 12 AS item_first_sales_app_past_14_days,
           29 AS item_has_sales_in_last_14_days, 1.428 AS item_percent_days_with_sales_last_14_days)
  ])
`)

publish("class_store_has_promo_sales_decay_sum_mock_2017614", { type: "table", tags: ["unit_test"] }).query(ctx => `
  SELECT * FROM UNNEST([
  STRUCT(1 AS store_nbr, 1000 AS class, 3.8765 AS class_store_has_sales_mean_7),
  STRUCT(2 AS store_nbr, 2000 AS class, 5.1 AS class_store_has_sales_mean_7),
  STRUCT(3 AS store_nbr, 1000 AS class, 1.709 AS class_store_has_sales_mean_7),
  STRUCT(4 AS store_nbr, 2000 AS class, 2.531 AS class_store_has_sales_mean_7)
  ])
`);