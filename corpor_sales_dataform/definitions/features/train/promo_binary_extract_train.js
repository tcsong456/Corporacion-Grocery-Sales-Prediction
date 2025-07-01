const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];

groups.forEach(group => {
    const keyGroup = group.join(",");
    const prefix = group.join("_").replace(/_nbr/g,'');
    const refTable = `partitioned_${prefix}_data`;
    dates.forEach(target_date => {
        const viewName = `${prefix}_future_promo_indicators_${target_date.replace(/-/g,'')}`;
        publish(viewName,{type:"view"}).query(ctx => `
                                                      SELECT
                                                      ${keyGroup},
                                                      SUM(onpromotion) promo_binary
                                                      FROM ${ctx.ref(refTable)}
                                                      WHERE date BETWEEN DATE('${target_date}') AND
                                                      DATE_ADD(DATE('${target_date}'),INTERVAL 15 DAY)
                                                      GROUP BY ${keyGroup}
                                                        `);
    });
});