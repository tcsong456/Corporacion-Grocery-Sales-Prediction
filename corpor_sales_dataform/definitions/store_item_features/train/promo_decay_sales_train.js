const { promo_decay_window } = require("includes/promo_window_decay_sales");
const windows = [3,7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const promo_conditions = ["=1","=0"];

promo_conditions.forEach(promoCondition => {
                         const promoFlag = promoCondition==="=1" ? "has_promo" : "no_promo";
                         dates.forEach(date => {
                                const viewName =  `${promoFlag}_sales_decay_sum_${date.replace(/-/g,'')}`
                                publish(viewName,{type: "view"}).query(ctx =>
                                                                       promo_decay_window(date,windows,0.9,promoCondition,
                                                                       ctx.ref("partitioned_full_data"),
                                                                       ["store_nbr","item_nbr"]));
    });
});