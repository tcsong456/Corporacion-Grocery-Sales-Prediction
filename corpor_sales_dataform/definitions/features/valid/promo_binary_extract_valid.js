const { promo_indicator_pivot } = require("includes/promo_indicators")
const date = '2017-7-26';
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const keyGroup = group.join(",");
    const prefix = group.join("_").replace(/_nbr/g,'');
    const refTable = `partitioned_${prefix}_data`;
    const viewName = `${prefix}_future_promo_indicators_${date.replace(/-/g,'')}`;
    publish(viewName,{type:"view"}).query(ctx => 
                                                promo_indicator_pivot(date,group,ctx.ref(refTable),prefix));
});