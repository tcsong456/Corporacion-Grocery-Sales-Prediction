const { promo_window } = require("includes/promo_window_sales");
const dates       = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const windows     = [3,7,14,30,60,140];

dates.forEach(date => {
  const viewName = `has_promo_sales_mean_${date.replace(/-/g,'')}`;
  const columns  = windows.map(w => promo_window(date, w)).join(",\n");
  publish(viewName, { type: "view" }).query(ctx => `
    SELECT
      store_nbr,
      item_nbr,
      ${columns}
    FROM ${ctx.ref("partitioned_full_data")}
    GROUP BY store_nbr, item_nbr
  `);
});
