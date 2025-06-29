const { promo_window } = require("includes/promo_window_sales");
const windows = [3,7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];
const promo_conditions = ["=1","=0"]

groups.forEach(group => {
    const keyCols = group.join(", ");
    const view_prefix = group.map(x => x.replace(/_nbr$/,'')).join('_');
    promo_conditions.forEach(promoCondition => {
        const promoFlag = promoCondition === "=1" ? "has_promo" : "no_promo";
        dates.forEach(date => {
                                const viewName = `${view_prefix}_${promoFlag}_sales_sum_${date.replace(/-/g,'')}`;
                                const columns = windows.map(w => promo_window(date,w,promoCondition)).join(",\n")
                                publish(viewName,{type: "view"}).query(ctx =>`
                                                                            SELECT
                                                                            ${keyCols},
                                                                            ${columns}
                                                                            FROM ${ctx.ref("partitioned_full_data")}
                                                                            GROUP BY ${keyCols}
                                                                        `);
        });
    });
});