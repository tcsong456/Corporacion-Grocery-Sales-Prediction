function promo_decay_window(targetDate,window_sizes,decay_rate,promoCondition,refTable,keyCols) {
    const promoFlag = promoCondition === ">0" ? "has_promo" : "no_promo";
    const keyColumns = keyCols.join(", ");
    const features = window_sizes.map(w => `SELECT
                                                ${keyColumns},
                                                SUM(CASE WHEN onpromotion ${promoCondition} THEN unit_sales ELSE NULL END
                                                    * POWER(${decay_rate},DATE_DIFF(DATE('${targetDate}'),date,DAY)-1))
                                                AS sales_decay_sum,
                                                ${w} AS source
                                                FROM ${refTable}
                                                WHERE date BETWEEN DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)
                                                AND DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)
                                                GROUP BY ${keyColumns}
                                                `
                                                ).join("\nUNION ALL\n");
    const columns = window_sizes.map(w => `
                                            MAX(CASE WHEN source=${w} THEN
                                            sales_decay_sum END) AS ${promoFlag}_sales_decay_sum_${w}`
                                            ).join(",\n");    
                                        
    return `WITH decay_window_sales_table AS 
            (${features})
            SELECT
            ${keyColumns},
            ${columns}
            FROM decay_window_sales_table
            GROUP BY ${keyColumns}
            `;
}

module.exports = { promo_decay_window }