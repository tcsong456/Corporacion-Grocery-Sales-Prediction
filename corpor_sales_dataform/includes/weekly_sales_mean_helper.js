function buildWeeklyDates(startDate,period) {
    const dates = [];
    const padding = n => String(n).padStart(2,'0');

    for (let i=0;i<period;i++) {
        const currentDate = new Date(startDate)
        currentDate.setDate(currentDate.getDate()+i*7)
        const y = currentDate.getUTCFullYear(),
              m = padding(currentDate.getUTCMonth()+1),
              dd = padding(currentDate.getUTCDate());
        const d = `${y}-${m}-${dd}`;
        dates.push(d)
    }
    return dates;
}

function weekly_sales_mean(startDates,period,prefix) {
    const meanDates = startDates.map(date => buildWeeklyDates(date,period));
    const columns = meanDates.map((meanDate,index) => {
        const meanDateStr = meanDate.map(d => `DATE('${d}')`).join(",");
        return `AVG(CASE WHEN date IN (${meanDateStr}) THEN unit_sales ELSE NULL END) AS ${prefix}_past_${period}_dow_mean_${index}`
    }).join(",\n")
    return columns;
}

module.exports = { weekly_sales_mean };