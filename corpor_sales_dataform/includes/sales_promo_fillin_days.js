function find_first_last(targetDate,targetCol,windows,keyCols,refTable,prefix) {
    const groupCol = keyCols.join(",")
    const columns = windows.flatMap(w => {
                                      const window_start = `DATE_SUB(DATE('${targetDate}'),INTERVAL ${w} DAY)`;
                                      const window_end = `DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)`;
                                      const sales_expr = `CASE WHEN date BETWEEN ${window_start} AND ${window_end}
                                                              AND unit_sales > 0 THEN 1 ELSE 0 END`;
                                      const target_flag = targetCol==="unit_sales" ? "sales" : "promo";
                                      const cols = [
                                                  `MIN(CASE WHEN date BETWEEN ${window_start} AND ${window_end} AND 
                                                  ${targetCol} > 0 THEN DATE_DIFF(DATE('${targetDate}'),date,DAY) - 1
                                                  ELSE NULL END)
                                                  AS ${prefix}_last_${target_flag}_app_past_${w}_days`,
                                                  `MAX(CASE WHEN date BETWEEN ${window_start} AND ${window_end} AND 
                                                  ${targetCol} > 0 THEN DATE_DIFF(DATE('${targetDate}'),date,DAY)
                                                  ELSE NULL END)
                                                  AS ${prefix}_first_${target_flag}_app_past_${w}_days`];
                                      if (targetCol==="unit_sales") {
                                          cols.push(`SUM(${sales_expr}) AS ${prefix}_has_sales_in_last_${w}_days`,
                                                      `SUM(${sales_expr}) / ${w} AS ${prefix}_percent_days_with_sales_last_${w}_days`);
                                      }
                                      return cols;
                                      
    }).join(",\n")
    return `SELECT
            ${groupCol},
            ${columns}
            FROM ${refTable}
            GROUP BY ${groupCol}
            `
};

module.exports = { find_first_last };