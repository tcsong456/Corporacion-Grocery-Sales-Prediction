publish('expected_concate_models', { type: "view", tags: ["unit_test"] }).query(ctx => `
  SELECT * FROM UNNEST([
    STRUCT(1 AS store_nbr, 10 AS item_nbr, 100 AS unit_sales, 1 AS onpromotion, 12 AS mean_sales_past_7, 5 AS promo_sum_past_14),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, 50 AS unit_sales, 1 AS onpromotion, 16.3 AS mean_sales_past_7, 2.91 AS promo_sum_past_14),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, 23.56 AS unit_sales, 0 AS onpromotion, 8.6 AS mean_sales_past_7, 1.01 AS promo_sum_past_14),
    STRUCT(1 AS store_nbr, 10 AS item_nbr, 90 AS unit_sales, 0 AS onpromotion, 10.5 AS mean_sales_past_7, 5.83 AS promo_sum_past_14),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, 50 AS unit_sales, 1 AS onpromotion, 15.2 AS mean_sales_past_7, 3.28 AS promo_sum_past_14),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, 27.961 AS unit_sales, 1 AS onpromotion, 8.6 AS mean_sales_past_7, 0.734 AS promo_sum_past_14),
    STRUCT(1 AS store_nbr, 10 AS item_nbr, 80 AS unit_sales, 1 AS onpromotion, 13.9 AS mean_sales_past_7, 2.83 AS promo_sum_past_14),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, 40 AS unit_sales, 0 AS onpromotion, 11.7 AS mean_sales_past_7, 4.28 AS promo_sum_past_14),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, 13.56 AS unit_sales, 0 AS onpromotion, 6.8 AS mean_sales_past_7, 2.734 AS promo_sum_past_14)
  ])
`);