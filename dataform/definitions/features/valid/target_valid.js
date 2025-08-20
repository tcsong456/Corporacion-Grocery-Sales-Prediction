const { generateDates } = require("includes/target_extractor");
const date = '2017-7-26';
publish("y_valid",{type:"view", tags: ["prod"]}).query(ctx => generateDates(date,16,ctx,"partitioned_store_item_data"))