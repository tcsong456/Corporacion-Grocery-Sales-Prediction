function generateDates(date,futureDays,ctx,target_dataset) {
  const dates = [];
  const padding = n => String(n).padStart(2,'0');
  const [y, m, d] = date.split('-').map(Number);
  const startDate = new Date(Date.UTC(y, m-1, d));
  
  for (let i=0;i<futureDays;i++) {
      const currentDate = new Date(startDate);
      currentDate.setUTCDate(currentDate.getUTCDate() + i);
      const y = currentDate.getUTCFullYear();
      const m = padding(currentDate.getUTCMonth() + 1);
      const d = padding(currentDate.getUTCDate());
      dates.push(`${y}-${m}-${d}`); 
  }
  dates.sort();
  const minDate = dates[0];
  const maxDate = dates[dates.length - 1];
  const columns = dates.map((d,i) => `MAX(CASE WHEN date=Date('${d}') THEN unit_sales ELSE NULL END) AS y${i}`).join(",\n");
  
  return `
          SELECT
          store_nbr,
          item_nbr,
          ${columns}
          FROM ${ctx.ref(target_dataset)}
          WHERE date BETWEEN Date('${minDate}')
          AND Date('${maxDate}')
          GROUP BY store_nbr,item_nbr    
          `
}

module.exports = { generateDates };


