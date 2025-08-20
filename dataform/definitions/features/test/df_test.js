const datasets = ['store_item_rolling_sales_stats',
                  'store_item_promo_first_last_app',
                  'item_promo_first_last_app',
                  'class_store_promo_first_last_app',
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
                  'item_rolling_sales_stats',
                  'class_store_rolling_sales_stats',
                  'store_item_dow_mean',
                  'item_dow_mean',
                  'class_store_dow_mean',
                  'store_item_sales_first_last_app',
                  'item_sales_first_last_app',
                  'class_store_sales_first_last_app'];
                  
const date = '2017-8-16';
const { merge_datasets } = require("includes/merge");

publish("raw_test",{type:"view", tags: ["prod"]}).query(ctx => merge_datasets(datasets,date,ctx,"store_item_class"));

publish("df_test",{type:"view", tags: ["prod"]}).query(ctx => `
                                                    SELECT * FROM(
                                                    SELECT
                                                    DISTINCT a.store_nbr,a.item_nbr,b.* EXCEPT(store_nbr,item_nbr)
                                                    FROM ${ctx.ref("test_data_table")} a
                                                    LEFT JOIN ${ctx.ref("raw_test")} b
                                                    ON a.store_nbr=b.store_nbr AND a.item_nbr=b.item_nbr) c
                                                    `)