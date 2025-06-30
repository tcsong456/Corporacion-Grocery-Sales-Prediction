const { find_first_last } = require("includes/sales_promo_fillin_days");
const windows = [7,14,30,60,140];
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];
const target_cols = ['unit_sales','onpromotion']

target_cols.forEach(targetcol=>{
    const targetFlag = targecol==='unit_sales' ? 'sales' : 'promo';
    groups.forEach(group => {
        dates.forEach(date => {
            const prefix = group.map(g=>g.replace(/_nbr$/,'')).join("_");
            const viewName = `${prefix}_${targetFlag}_frist_last_app_${date.replace(/-/g,'')}`;
            publish(viewName,{type:"view"}).query(cty=>
                                                        find_first_last(date,targetcol,windows,group,
                                                                        ctx.ref("partitioned_full_data"))
                                                    );
        });
    });
});
