const { weekly_sales_mean } = require('../../corpor_sales_dataform/includes/weekly_sales_mean_helper');

describe('test sql generation for weekly_sales_mean', () => {
    it('sql generation for item with period size of 4', () => {
        const sql = weekly_sales_mean(['2017-5-16','2017-5-18'],4,'item');
        expect(sql).toMatch(/AVG\(CASE WHEN date IN \(DATE\('2017-05-16'\),DATE\('2017-05-23'\),DATE\('2017-05-30'\),DATE\('2017-06-06'\)\)/);
        expect(sql).toMatch(/item_past_4_dow_mean_0/);
        expect(sql).toMatch(/AVG\(CASE WHEN date IN \(DATE\('2017-05-18'\),DATE\('2017-05-25'\),DATE\('2017-06-01'\),DATE\('2017-06-08'\)\)/);
        expect(sql).toMatch(/item_past_4_dow_mean_1/);
    });
    
    it('sql generation for class_store with period size of 6', () => {
        const sql = weekly_sales_mean(['2017-5-16','2017-5-18'],6,'class_store');
        expect(sql).toMatch(/AVG\(CASE WHEN date IN \(DATE\('2017-05-16'\),DATE\('2017-05-23'\),DATE\('2017-05-30'\),DATE\('2017-06-06'\),DATE\('2017-06-13'\),DATE\('2017-06-20'\)\)/);
        expect(sql).toMatch(/class_store_past_6_dow_mean_0/);
    });
});