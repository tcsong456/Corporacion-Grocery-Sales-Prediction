function promo_window(targetDate,window_size,promoCond,prefix) {
    const startDate = `DATE_SUB(DATE '${targetDate}',INTERVAL ${window_size} DAY)`;
    const endDate = `DATE_SUB(DATE '${targetDate}',INTERVAL 1 DAY)`;
    const colMid = promoCond===">0" ? "has_promo" : "no_promo";
    
    return `AVG(CASE WHEN onpromotion ${promoCond} AND date BETWEEN
                ${startDate} AND ${endDate}  
                THEN unit_sales
                ELSE NULL
                END) AS ${prefix}_${colMid}_mean_${window_size}`;
}

module.exports = { promo_window };