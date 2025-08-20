const { rolling_window_stats } = require("includes/sales_window_stats");
const windows = [3,7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const view_prefix = group.join("_").replace(/_nbr/g,"");
    const refTable = `partitioned_${view_prefix}_data`;
    dates.forEach(date => {
                          const viewName = `${view_prefix}_rolling_sales_stats_${date.replace(/-/g,'')}`;
                          publish(viewName,{type: "view", tags: ["prod"]}).query(ctx => 
                                                                      rolling_window_stats(date,windows,0.9,
                                                                      group,
                                                                      ctx.ref(refTable),view_prefix)
                          );
    });
});