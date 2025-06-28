function rolling_window_stats(targetDate,window_sizes,decay_rate,keyCols,refTable) {
    const keyColumns = keyCols.join(", ");
    const features = window_sizes.map(w => `SELECT
                                             ${keyColumns},
                                             MIN(unit_sales) AS unit_sales_min,
                                             MAX(unit_sales) AS unit_sales_max,
                                             AVG(unit_sales) AS unit_sales_mean,
                                             PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY unit_sales) AS unit_sales_median,
                                             STDDEV_SAMP(unit_sales) AS unit_sales_std,
                                             SUM(unit_sales *
                                             POWER(${decay_rate},DATE_DIFF(DATE('${targetDate}'),date,DAY)-1)) AS unit_sales_dcay_sum,
                                             ${w} as source
                                             FROM ${refTable}
                                             WHERE date BETWEEN
                                             DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)
                                             AND
                                             DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)
                                             GROUP BY ${keyColumns}
                                             `).join("\nUNION ALL\n");
    const columns = window_sizes.flatMap(w => {
                                                return [
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_min) AS unit_sales_min_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_max) AS unit_sales_max_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_mean) AS unit_sales_mean_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_median) AS unit_sales_median_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_std) AS unit_sales_std_${w}`,
                                                `MAX(CASE WHEN source=${w} THEN unit_sales_dcay_sum) AS unit_sales_dcay_sum_${w}`
                                                ]                                        
                                        }).join(",\n");
    return `WITH feature_table AS
            (${features})
            SELECT
            ${keyColumns},
            ${columns}
            FROM feature_table
            GROUP BY ${keyColumns};
        `
};

module.exports = { rolling_window_stats }