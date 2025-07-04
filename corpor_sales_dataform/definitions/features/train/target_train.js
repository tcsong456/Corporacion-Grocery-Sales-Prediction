const { generateDates } = require("includes/target_extractor");
const dates = ['2017-6-14','2017-6-21','2017-6-28','2017-7-05','2017-7-12','2017-7-19'];

dates.forEach(date => {
                const viewName = `y_${date.replace(/-/g,'')}`;
                publish(viewName,{type:"view"}).query(ctx => generateDates(date,16,ctx));
})

publish("y_train",{type:"view"}).query(ctx => `
                                            ${dates.map((date,i) => `
                                                   ${i>0 ? "UNION ALL\n" :""}SELECT * FROM ${ctx.ref(`y_${date.replace(/-/g,'')}`)}
                                            `).join("\n")}
                                        `);