function promo_window(targetDate,window_size,promoCond) {
    const startDate = `DATE_SUB(DATE '${targetDate}',INTERVAL ${window_size} DAY)`;
    const endDate = `DATE_SUB(DATE '${targetDate}',INTERVAL 1 DAY)`;
    const colPrefix = promoCond===">0" ? "has_promo" : "no_promo";
    
    return `AVG(CASE WHEN onpromotion ${promoCond} AND date BETWEEN
                ${startDate} AND ${endDate}  
                THEN unit_sales
                ELSE NULL
                END) AS ${colPrefix}_mean_${window_size}`;
}

module.exports = { promo_window };