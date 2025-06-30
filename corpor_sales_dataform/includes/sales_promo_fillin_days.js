function find_first_last(targetDate,targeCol,windows,keyCols,refTable) {
    const groupCol = keyCols.join(",")
    const columns = windows.flatMap(w => {
                                      const window_start = `DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)`;
                                      const window_end = `DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)`;
                                      const sales_expr = `CASE WHEN date BETWEEN ${window_start} AND ${window_end}
                                                              AND unit_sales > 0 THEN 1 ELSE 0 END`;
                                      const target_flag === targetCol="unit_sales" ? "sale" : "promo";
                                      columns = [
                                                  `MAX(CASE WHEN date BETWEEN ${window_start} AND ${window_end} AND 
                                                  ${targetCol} > 0 THEN ${w} - DATE_DIFF(DATE('${targetDate}'),date,DAY))
                                                  AS last_${target_flag}_app_past_${w}_days`,
                                                  `MIN(CASE WHEN date BETWEEN ${window_start} AND ${window_end} AND 
                                                  ${targetCol} > 0 THEN DATE_DIFF(DATE('${targetDate}'),date,DAY))
                                                  AS first_${target_flag}_app_past_${w}_days`]
                                      if (targetCol==="unit_sales") {
                                          columns.push(`SUM(${sales_expr}) AS has_sales_in_last_${w}_days`,
                                                      `SUM(${sales_expr}) / ${w} AS percent_days_with_sales_last_${w}_days`)
                                      };
                                      return columns;
                                      
    }).join(",\n")
    return `SELECT,
            ${groupCol},
            ${columns}
            FROM ${refTable}
            GROUP BY ${groupCol}
            `
};

module.exports = { find_first_last };