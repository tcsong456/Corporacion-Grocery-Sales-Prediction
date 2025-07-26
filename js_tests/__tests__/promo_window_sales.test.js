const { promo_window } = require("../../corpor_sales_dataform/includes/promo_window_sales")

describe('test sql script for promo sales', () => {
    it('sql generation for sales with promotions on window size of 7 days', () => {
        const sql = promo_window('2017-6-21',[7],">0","store_item");
        expect(sql).toMatch(/AVG\(CASE WHEN onpromotion >0 AND date BETWEEN/);
        expect(sql).toMatch(/DATE_SUB\(DATE '2017-6-21',INTERVAL 7 DAY\)/);
        expect(sql).toMatch(/DATE_SUB\(DATE '2017-6-21',INTERVAL 1 DAY\)/);
        expect(sql).toMatch(/AS store_item_has_promo_mean_7/);
    });
    
    it('sql generation for sales with no promotion on window size of 14 days', () => {
        const sql = promo_window('2017-6-28',[14],"=0","class_store");
        expect(sql).toMatch(/AVG\(CASE WHEN onpromotion =0 AND date BETWEEN/);
        expect(sql).toMatch(/DATE_SUB\(DATE '2017-6-28',INTERVAL 14 DAY\)/);
        expect(sql).toMatch(/DATE_SUB\(DATE '2017-6-28',INTERVAL 1 DAY\)/);
        expect(sql).toMatch(/AS class_store_no_promo_mean_14/);
    });
});