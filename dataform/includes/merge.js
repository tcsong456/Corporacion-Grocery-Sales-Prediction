function merge_datasets(datasets,date,ctx,target_ds) {
    const keys = {
                    store_item:['store_nbr','item_nbr'],
                    item:['item_nbr'],
                    class_store:['class','store_nbr']
                    };
    const baseDataset = "t0";
    const joins = datasets.map((dataset,i) => {
                            const match = Object.keys(keys).find(prefix=> dataset.startsWith(prefix));
                            if (!match) {
                                        throw new Error(`No join key found for dataset: "${dataset}"`);
                                }
                            const keyJoin = keys[match];
                            const conditions = keyJoin.map(keyjoin => `${baseDataset}.${keyjoin}=t${i+1}.${keyjoin}`).join(" AND ");
                            const tableName = `${dataset}_${date.replace(/-/g,'')}`;
                            return `LEFT JOIN ${ctx.ref(tableName)} t${i+1} ON ${conditions}`;
                            }).join("\n");
    const selectColumns = datasets.map((dataset,i) => {
                            const match = Object.keys(keys).find(prefix=> dataset.startsWith(prefix));
                            if (!match) {
                                        throw new Error(`No join key found for dataset: "${dataset}"`);
                                }
                            const keyJoin = keys[match];
                            const otherColumns = `t${i+1}.* EXCEPT(${keyJoin.join(",")})`
                            return otherColumns;
                                })
    const columns = [`t0.store_nbr`,`t0.item_nbr`,...selectColumns].join(",\n");
    return `
            SELECT
            ${columns}
            FROM ${ctx.ref(target_ds)} t0
            ${joins}
            `
}

module.exports = { merge_datasets };
