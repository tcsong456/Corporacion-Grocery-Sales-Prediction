const { generateDates } = require("includes/target_extractor");
const date = '2017-7-26';
publish("y_valid_raw",{type:"view", tags: ["prod"]}).query(ctx => generateDates(date,16,ctx,"partitioned_store_item_data"))
publish("y_valid",{type:"view", tags: ["prod"]}).query(ctx => `
                                                    SELECT * FROM(
                                                    SELECT
                                                    DISTINCT a.store_nbr,a.item_nbr,b.* EXCEPT(store_nbr,item_nbr)
                                                    FROM ${ctx.ref("test_data_table")} a
                                                    LEFT JOIN ${ctx.ref("y_valid_raw")} b
                                                    ON a.store_nbr=b.store_nbr AND a.item_nbr=b.item_nbr) c
                                                    `)