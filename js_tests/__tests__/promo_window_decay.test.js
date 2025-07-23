const { promo_decay_window } = require("../../corpor_sales_dataform/includes/promo_window_decay_sales")

describe('test sql generation for promo decay sales', () => {
    it('item sql script for has_promo situation', () => {
        const sql = promo_decay_window('2017-6-21',[14],0.9,">0","partitioned_item_data",['item_nbr'],'item');
        expect(sql).toMatch(/SUM\(CASE WHEN onpromotion >0 THEN unit_sales ELSE NULL END/);
        expect(sql).toMatch(/POWER\(0.9,DATE_DIFF\(DATE\('2017-6-21'\),date,DAY\)-1\)/);
        expect(sql).toMatch(/WHERE date BETWEEN DATE_SUB\(DATE\('2017-6-21'\),INTERVAL 14 DAY\)/);
        expect(sql).toMatch(/\s+DATE_SUB\(DATE\('2017-6-21'\),INTERVAL 1 DAY\)\s+GROUP BY item_nbr/);
        expect(sql).toMatch(/MAX\(CASE WHEN source=14 THEN\s+sales_decay_sum END\) AS item_has_promo_sales_decay_sum_14/);
    });
    
    it('store_item sql script for no_promo situation', () => {
        const sql = promo_decay_window('2017-6-21',[30],0.9,"=0","partitioned_item_data",['store_nbr','item_nbr'],'store_item');
        expect(sql).toMatch(/CASE WHEN onpromotion =0 THEN unit_sales ELSE NULL END/);
        expect(sql).toMatch(/WHERE date BETWEEN DATE_SUB\(DATE\('2017-6-21'\),INTERVAL 30 DAY\)/);
        expect(sql).toMatch(/\s+DATE_SUB\(DATE\('2017-6-21'\),INTERVAL 1 DAY\)\s+GROUP BY store_nbr, item_nbr/);
        expect(sql).toMatch(/MAX\(CASE WHEN source=30 THEN\s+sales_decay_sum END\) AS store_item_no_promo_sales_decay_sum_30/);
    });
});