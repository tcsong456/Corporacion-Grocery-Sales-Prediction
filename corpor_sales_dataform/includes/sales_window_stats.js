function rolling_window_stats(targetDate,window_sizes,decay_rate,keyCols,refTable,prefix) {
    const keyColumns = keyCols.join(", ");
    const features = window_sizes.map(w => `SELECT
                                             ${keyColumns},
                                             MIN(unit_sales) AS unit_sales_min,
                                             MAX(unit_sales) AS unit_sales_max,
                                             AVG(unit_sales) AS unit_sales_mean,
                                             APPROX_QUANTILES(unit_sales,2)[OFFSET(1)] AS unit_sales_median,
                                             STDDEV_SAMP(unit_sales) AS unit_sales_std,
                                             SUM(unit_sales *
                                             POWER(${decay_rate},DATE_DIFF(DATE('${targetDate}'),date,DAY)-1)) AS unit_sales_decay_sum,
                                             ${w} AS source
                                             FROM ${refTable}
                                             WHERE date BETWEEN
                                             DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)
                                             AND
                                             DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)
                                             GROUP BY ${keyColumns}
                                             `).join("\nUNION ALL\n");
    const columns = window_sizes.flatMap(w => {
                                                return [
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_min END) AS ${prefix}_unit_sales_min_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_max END) AS ${prefix}_unit_sales_max_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_mean END) AS ${prefix}_unit_sales_mean_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_median END) AS ${prefix}_unit_sales_median_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_std END) AS ${prefix}_unit_sales_std_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_decay_sum END) AS ${prefix}_unit_sales_decay_sum_${w}`
                                                ]                                        
                                        }).join(",\n");
    return `WITH feature_table AS
            (${features})
            SELECT
            ${keyColumns},
            ${columns}
            FROM feature_table
            GROUP BY ${keyColumns}
        `;
};

module.exports = { rolling_window_stats }
