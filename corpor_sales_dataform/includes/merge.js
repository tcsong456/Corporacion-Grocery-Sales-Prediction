function merge_datasets(datasets,date) {
    const keys = {
                    store_item:['store_nbr','item_nbr'],
                    item:['item_nbr'],
                    class_store:['class','store_nbr']
                    };
    const baseDataset = "t0";
    datasets.slice(1).map((dataset,i) => {
                            const match = Object.keys(keys).find(prefix=> dataset.startswith(prefix));
                            if (!match) {
                                        console.error(`no join key found for dataset:"${dataset}"`);
                                        process.exit(1);
                                }
                            const keyJoin = keys[match];
                            const condition = keyJoin.map(keyjoin => `${baseDataset}.${keyjoin}=t{i+1}.${keyjoin}`).join(" AND ")
                            return `LEFT JOIN ${ref("${dataset}_${date.replace(/-/g,'')}")} ON ${conditions}`
                            })
}