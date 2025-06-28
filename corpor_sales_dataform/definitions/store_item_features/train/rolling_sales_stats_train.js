const { rolling_window_stats } = require("includes/sales_window_stats");
const windows = [3,7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];

dates.forEach(date => {
                      const viewName = `rolling_sales_stats_${date.replace(/-/g,'')}`
                      publish(viewName,{type: "view"}).query(ctx => {
                                                                  rolling_window_stats(date,windows,0.9,
                                                                  ["store_nbr","item_nbr"],
                                                                  ctx.ref("partitioned_full_data"))
                      });
});