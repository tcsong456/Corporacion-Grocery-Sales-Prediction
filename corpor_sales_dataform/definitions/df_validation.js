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
const dates = ['2017-7-26'];
const { merge_datasets } = require("includes/merge");


publish("df_validation",{type:"view"}).query(ctx => merge_datasets(datasets,date,ctx));

