const { find_first_last } = require("includes/sales_promo_fillin_days");
const windows = [7,14,30,60,140];
const date = '2017-8-16';
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];
const target_cols = ["unit_sales","onpromotion"]

target_cols.forEach(targetcol=>{
    const targetFlag = targetcol==='unit_sales' ? 'sales' : 'promo';
    groups.forEach(group => {
        const prefix = group.map(g=>g.replace(/_nbr$/,'')).join("_");
        const refTable = `partitioned_${prefix}_data`;
        const viewName = `${prefix}_${targetFlag}_first_last_app_${date.replace(/-/g,'')}`;
        publish(viewName,{type:"view", tags: ["prod"]}).query(ctx =>
                                                    find_first_last(date,targetcol,windows,group,
                                                                    ctx.ref(refTable),prefix)
                                                );
});
});
