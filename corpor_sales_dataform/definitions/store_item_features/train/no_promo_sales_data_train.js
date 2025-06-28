const { no_promo_window } = require("includes/promo_window_sales");
const windows = [3,7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];

dates.forEach(date => {
                        const viewName = `no_promo_sales_sum_${date.replace(/-/,'')}`;
                        const columns = windows.map(w => no_promo_window(date,w)).join(",\n")
                        publish(viewName,{type: "view"}).query(ctx =>`
                                                                    SELECT
                                                                    store_nbr,
                                                                    item_nbr,
                                                                    ${columns}
                                                                    FROM ${ctx.ref("partitioned_full_data")}
                                                                    GROUP BY store_nbr,item_nbr
                            `);
})