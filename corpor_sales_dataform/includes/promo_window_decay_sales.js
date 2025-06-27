function promo_decay_window(targetDate,window_sizes,decay_rate,promoCondition,refTable) {
    const promoFlag = promoCondition === "=1" ? "promo" : "no_promo";
    const features = window_sizes.map(w => `SELECT
                                                store_nbr,
                                                item_nbr,
                                                AVG(CASE WHEN onpromotion ${promoCondition} THEN unit_sales ELSE NULL END
                                                    * POWER(${decay_rate},DATE_DIFF(DATE('${targetDate}'),date,DAY)-1))
                                                AS sales_decay_mean,
                                                ${w} AS source
                                                FROM ${refTable}
                                                WHERE date BETWEEN DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)
                                                AND DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)
                                                GROUP BY store_nbr,item_nbr
                                                `
                                                ).join("\nUNION ALL\n");
    const columns = window_sizes.map(w => `
                                            MAX(CASE WHEN source=${w} THEN
                                            sales_decay_mean END) AS ${promoFlag}_sales_decay_mean_${w}`
                                            ).join(",\n");    
                                        
    return `WITH decay_window_sales_table AS 
            (${features})
            SELECT
            store_nbr,
            item_nbr,
            ${columns}
            FROM decay_window_sales_table
            GROUP BY store_nbr,item_nbr
            `;
}

module.exports = { promo_decay_window }