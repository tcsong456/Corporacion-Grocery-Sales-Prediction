function promo_indicator_pivot(startDate,keyCol,refTable,prefix) {
    const dates = [];
    const groupCol = keyCol.join(",");
    const padding = n =>  String(n).padStart(2,'0');
    const d0 = new Date(startDate),d1 = new Date(d0);
    d1.setDate(d1.getDate() + 15);
    
    for (let d=new Date(d0);d<=d1;d.setDate(d.getDate()+1)) {
        const y = d.getUTCFullYear(),
              m = padding(d.getUTCMonth() + 1),
              dd = padding(d.getUTCDate());
        dates.push(`${y}-${m}-${dd}`)
    }
    
    const columns = dates.map((d,index) => {
        const col =  `${prefix}_promo_${index}`;
        
        return `
                MAX(CASE WHEN date=DATE('${d}') THEN onpromotion ELSE NULL END) AS ${col}
                `
    }).join(",\n");
    return `
            SELECT
            ${groupCol},
            ${columns}
            FROM
            ${refTable}
            WHERE date BETWEEN DATE('${dates[0]}') AND DATE('${dates[dates.length-1]}')
            GROUP BY ${groupCol}
    `
}

module.exports = { promo_indicator_pivot };