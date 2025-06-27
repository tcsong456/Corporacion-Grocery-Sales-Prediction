function promo_window(targetDate,window_size) {
    const startDate = `DATE_SUB(DATE '${targetDate}',INTERVAL ${window_size} DAY)`;
    const endDate = `DATE_SUB(DATE '${targetDate}',INTERVAL 1 DAY)`;
    
    return `AVG(CASE WHEN onpromotion > 0 AND date BETWEEN
                ${startDate} AND ${endDate}  
                THEN unit_sales
                ELSE NULL
                END) AS has_promo_mean_${window_size}`;
}

function no_promo_window(targetDate,window_size) {
    const startDate = `DATE_SUB(DATE '${targetDate}',INTERVAL ${window_size} DAY)`
    const endDate = `DATE_SUB(DATE '${targetDate}',INTERVAL 1 DAY)`
    return `
          AVG(CASE WHEN onpromotion=0 AND date between ${startDate} AND ${endDate}
               THEN unit_sales
               ELSE NULL
               END) AS no_promo_sales_${window_size}
        `;
}
module.exports = { promo_window,
                   no_promo_window };