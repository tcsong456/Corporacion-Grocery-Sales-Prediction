const { merge_datasets } = require("../../corpor_sales_dataform/includes/merge")

datasets = [
  'store_item_rolling_sales_stats',
  'item_promo_first_last_app',
  'class_store_future_promo_indicators'
]

const ctx = {
  ref: (name) => `\`${name}\``
};

describe('sql generation test', () => {
  it('join keys test', () => {
    const sql = merge_datasets(datasets,'2017-6-14',ctx,'store_item_class_mock_2017614');
    expect(sql).toMatch('LEFT JOIN `store_item_rolling_sales_stats_2017614` t1 ON t0.store_nbr=t1.store_nbr AND t0.item_nbr=t1.item_nbr');
    expect(sql).toMatch('LEFT JOIN `item_promo_first_last_app_2017614` t2 ON t0.item_nbr=t2.item_nbr');
  });
  it('select columns test', () => {
    const sql = merge_datasets(datasets,'2017-6-14',ctx,'store_item_class_mock_2017614');
    expect(sql).toMatch('t0.store_nbr,\nt0.item_nbr,\nt1.* EXCEPT\(store_nbr,item_nbr\)');
    expect(sql).toMatch('t3.* EXCEPT\(class,store_nbr\)');
  });
});