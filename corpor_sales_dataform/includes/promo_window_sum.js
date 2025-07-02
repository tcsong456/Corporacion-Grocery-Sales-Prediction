function promo_window_sum(targetDate,windows,keyCols,refTable,prefix) {
    const groupCols = keyCols.join(",")
    const columns = windows.flatMap(w => {
                                        const suffix = w >= 0 ? `past_${w}` : `future_${Math.abs(w)}`;
                                        const window_start = w >= 0 ? `DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)` :
                                                                      `DATE('${targetDate}')`;
                                        const window_end = w >= 0 ? `DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)` :
                                                                    `DATE_ADD(DATE('${targetDate}'),INTERVAL ${Math.abs(w)} DAY)`;
                                        const columns = [`SUM(CASE WHEN date BETWEEN ${window_start} AND ${window_end}
                                                         THEN onpromotion ELSE 0 END) AS ${prefix}_promo_sum_${suffix}`];
                                        if (w>=0) {
                                            columns.push(`SUM(CASE WHEN date BETWEEN ${window_start} AND ${window_end}
                                                          THEN onpromotion ELSE 0 END) / ${Math.abs(w)} AS ${prefix}_promo_mean_${suffix}`);
                                        }
                                        return columns;
                                                
    }).join(",\n")
    return `SELECT
            ${groupCols},
            ${columns}
            FROM ${refTable}
            GROUP BY ${groupCols}
            `
};

module.exports = { promo_window_sum }