const { promo_window_sum } = require("../../corpor_sales_dataform/includes/promo_window_sum")

describe('test sql generation for promo window sum', () => {
    it('sql script for promo_sums on window size of -7 for item', () => {
        const sql = promo_window_sum('2017-7-05',[-7],['item_nbr'],'partitioned_item_data','item');
        expect(sql).toMatch(/SUM\(CASE WHEN date BETWEEN DATE\('2017-7-05'\) AND DATE_ADD\(DATE\('2017-7-05'\),INTERVAL 7 DAY\)/);
        expect(sql).toMatch(/item_promo_sum_future_7/);
    });
    
    it('sql script for promo_sums on window size of 14 for class store', () => {
        const sql = promo_window_sum('2017-7-05',[14],['class','store_nbr'],'partitioned_item_data','class_store');
        expect(sql).toMatch(/SUM\(CASE WHEN date BETWEEN DATE_SUB\(DATE\('2017-7-05'\),INTERVAL 14 DAY\)/);
        expect(sql).toMatch(/class_store_promo_sum_past_14/);
        expect(sql).toMatch(/THEN onpromotion ELSE 0 END\) \/ 14/);
        expect(sql).toMatch(/class_store_promo_mean_past_14/);
    });
});