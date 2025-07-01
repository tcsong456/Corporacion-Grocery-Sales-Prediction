function promo_indicator_pivot(startDate,endDate) {
    const dates = [];
    const padding = n =>  String(n).padString(2,'0');
    const d0 = new Date(startDate),d1 = new Date(endDate);
    for (let d=new Date(d0);d<d1;d.setDate(d.getDate()+1)) {
        const y = d.getUTCFullYear(),
              m = padding(d.getUTCMonth() + 1),
              d = padding(d.getUTCDate());
        dates.push(`${y}-${m}-${d}`)
    }
    const columns = dates.map((_,index) => {
        const col =  `promo_${index}`
    })   
}