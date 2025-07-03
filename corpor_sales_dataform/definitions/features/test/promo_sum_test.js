const { promo_window_sum } = require("includes/promo_window_sum");
const windows = [-3,-7,-15,7,14,30,60,140];
const date = '2017-8-16';
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const table_prefix = group.join("_").replace(/_nbr/g,"");
    const refTable = `partitioned_${table_prefix}_data`;
    const viewName = `${table_prefix}_promo_sum_${date.replace(/-/g,'')}`;
    publish(viewName,{type:"view"}).query(ctx => promo_window_sum(date,windows,group,
                                                                  ctx.ref(refTable),table_prefix));
    });