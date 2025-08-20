function dateConversion(date) {
    const padding = n => String(n).padStart(2,'0');
    const y = date.getUTCFullYear(),
          m = padding(date.getUTCMonth()+1),
          dd = padding(date.getUTCDate());
    return `${y}-${m}-${dd}`;
}

function buildPastDates(endDate,period) {
    const dates = [];
    const d = new Date(endDate);
    d.setDate(d.getDate() - 1);
    const time_span = 7 * period;
    
    for (let i=0;i<7;i++) {
        const currentDate = new Date(d)
        currentDate.setDate(currentDate.getDate() - time_span + i)
        dates.push(dateConversion(currentDate))
    }
    return dates;
}

const { weekly_sales_mean } = require("includes/weekly_sales_mean_helper")
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];
const groups = [["item_nbr"],["class","store_nbr"],["store_nbr","item_nbr"]];
const periods = [4,10,20]

groups.forEach(group => {
    const prefix = group.join("_").replace(/_nbr/g,"");
    const groupCol = group.join(",");
    const refTable = `partitioned_${prefix}_data`;
    dates.forEach(date => {
        const allDates = [];
        const allColumns = [];
        periods.forEach(period => {
            const validDates = buildPastDates(date,period);
            const columns = weekly_sales_mean(validDates,period,prefix);
            allDates.push(...validDates);
            allColumns.push(columns);
            });
        const viewName = `${prefix}_dow_mean_${date.replace(/-/g,'')}`;
        allDates.sort();
        const minDate = allDates[0];
        const maxDate = allDates[allDates.length-1];
        publish(viewName,{type:"view", tags: ["prod"]}).query(ctx =>`SELECT
                                                      ${groupCol},
                                                      ${allColumns}
                                                      FROM ${ctx.ref(refTable)}
                                                      WHERE date BETWEEN DATE('${minDate}') AND DATE('${maxDate}')
                                                      GROUP BY ${groupCol}
                                                    `);
            }); 
        });