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
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const { merge_datasets } = require("includes/merge");

dates.forEach(date => {
    const viewName = `merge_features_${date.replace(/-/g,'')}`;
    publish(viewName,{type:"view"}).query(ctx => merge_datasets(datasets,date,ctx))
})

publish("df_train",{type:"view"}).query(ctx => `
                                        ${dates.map((date,i) => `
                                               ${i >0 ? "UNION ALL\n" : ""}SELECT * FROM 
                                                           ${ctx.ref(`merge_features_${date.replace(/-/g,'')}`)}     
                                            `).join("\n")}                    
                                        `);
