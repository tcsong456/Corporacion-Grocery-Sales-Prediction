const { promo_decay_window } = require("includes/promo_window_decay_sales");
const windows = [3,7,14,30,60,140];
const date = '2017-7-26';
const promo_conditions = [">0","=0"];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const view_prefix = group.join("_").replace(/_nbr/g,"");
    const refTable = `partitioned_${view_prefix}_data`;
    promo_conditions.forEach(promoCondition => {
                             const promoFlag = promoCondition===">0" ? "has_promo" : "no_promo";
                             const viewName =  `${view_prefix}_${promoFlag}_sales_decay_sum_${date.replace(/-/g,'')}`
                             publish(viewName,{type: "view", tags: ["prod"]}).query(ctx =>
                                                                   promo_decay_window(date,windows,0.9,promoCondition,
                                                                   ctx.ref(refTable),
                                                                   group,view_prefix));
        });
});