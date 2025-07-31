const { generateDates } = require("../../corpor_sales_dataform/includes/target_extractor");

const ctx = {
  ref: (name) => `\`${name}\``
};

describe('sql generation test', () => {
  it('column test', () => {
    const sql = generateDates('2017-6-14', 16, ctx, 'partitioned_store_item_data');
    expect(sql).toMatch(/MAX\(CASE WHEN date=Date\('2017-06-14'\) THEN unit_sales ELSE NULL END\) AS y0/);
    expect(sql).toMatch(/MAX\(CASE WHEN date=Date\('2017-06-18'\) THEN unit_sales ELSE NULL END\) AS y4/);
    expect(sql).toMatch(/MAX\(CASE WHEN date=Date\('2017-06-29'\) THEN unit_sales ELSE NULL END\) AS y15/);
  });
  
  it('date range scan test', () => {
    const sql = generateDates('2017-6-14', 16, ctx, 'partitioned_store_item_data');
    expect(sql).toMatch(/WHERE date BETWEEN Date\('2017-06-14'\)\s+AND Date\('2017-06-29'\)\s+GROUP BY store_nbr,item_nbr/);
  });
});