const { rolling_window_stats } = require("includes/sales_window_stats");
const windows = [3,7,14,30,60,140];
const date = '2017-8-16';
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const view_prefix = group.join("_").replace(/_nbr/g,"");
    const refTable = `partitioned_${view_prefix}_data`;
    const viewName = `${view_prefix}_rolling_sales_stats_${date.replace(/-/g,'')}`;
    publish(viewName,{type: "view", tags: ["prod"]}).query(ctx => 
                                                rolling_window_stats(date,windows,0.9,
                                                group,
                                                ctx.ref(refTable),view_prefix)
                          );
});