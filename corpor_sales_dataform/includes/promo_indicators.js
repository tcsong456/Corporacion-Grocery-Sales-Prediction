function promo_window_sum(targetDate,windows,keyCols,refTable) {
    const windowList = `[${ windows.join(",") }]`];
    const dynamicSelectCols = keyCols.map(k => `b.${k}`).join(",")
    const pivotAlias = windows.map(w => {
                                        const alias = w >=0 ? `past_${w}` : `future_${Math.abs(w)}`;
                                        return `${w} AS ${alias}`;
                }).join(",");
    return    `
                WITH date_windows AS (
                SELECT
                DATE('${targetDate}') AS target_date,
                w AS window_size,
                CASE WHEN  w >=0 THEN DATE_SUB(DATE('${targetDate}'),INTERVAL w DAY)
                                  ELSE DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY) END AS window_start,
                CASE WHEN w < 0 THEN DATE_SUB(DATE('${targetDate}'),INTERVAL 1 DAY)
                                 ELSE DATE_ADD(DATE('${targetDate}'),INTERVAL ABS(w) DAY) END AS window_end
                FROM UNNEST(${windowList}) AS w
                ),
                df AS(
                SELECT
                ${dynamicSelectCols},
                b.onpromotion,
                a.window_size
                FROM
                date_windows AS a JOIN
                ${refTable} AS b ON
                b.date BETWEEN a.window_start AND a.window_end
                )
                SELECT
                *
                FROM df
                PIVOT(
                SUM(onpromotion) AS promo_sum,
                AVG(onpromotion) AS promo_mean
                FOR window_size IN (${pivotAlias})
                )
                `;
};

module.exports = { promo_window_sum }