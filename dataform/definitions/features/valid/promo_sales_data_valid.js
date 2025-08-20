const { promo_window } = require("includes/promo_window_sales");
const windows = [3,7,14,30,60,140];
const date = '2017-7-26';
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];
const promo_conditions = [">0","=0"]

groups.forEach(group => {
    const keyCols = group.join(", ");
    const view_prefix = group.map(x => x.replace(/_nbr$/,'')).join('_');
    const refTable = `partitioned_${view_prefix}_data`;
    promo_conditions.forEach(promoCondition => {
        const promoFlag = promoCondition === ">0" ? "has_promo" : "no_promo";
        const viewName = `${view_prefix}_${promoFlag}_sales_sum_${date.replace(/-/g,'')}`;
        const columns = windows.map(w => promo_window(date,w,promoCondition,view_prefix)).join(",\n")
        publish(viewName,{type: "view", tags: ["prod"]}).query(ctx =>`
                                                    SELECT
                                                    ${keyCols},
                                                    ${columns}
                                                    FROM ${ctx.ref(refTable)}
                                                    GROUP BY ${keyCols}
                                                `);
    });
});