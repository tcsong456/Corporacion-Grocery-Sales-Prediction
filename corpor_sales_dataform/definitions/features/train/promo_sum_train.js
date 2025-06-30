const { promo_window_sum } = require("includes/promo_indicators");
const windows = [-3,-7,-14,7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const table_prefix = group.join("_").replace(/_nbr/g,"")
    dates.forEach(date => {
        const viewName = `${table_prefix}_promo_sum_${date.replace(/-/g,'')}`;
        publish(viewName,{type:"view"}).query(ctx => promo_window_sum(date,windows,group,
                                                                      ctx.ref("partitioned_full_data"))
        );
    });
});