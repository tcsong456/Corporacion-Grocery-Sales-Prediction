const { find_first_last } = require("../../corpor_sales_dataform/includes/sales_promo_fillin_days")

describe('test find_frist_last sql generation', () => {
    it('generate sql script for 7-day window on unit_sales', () => {
        const sql = find_first_last('2024-01-01', 'unit_sales', [7], ['store_nbr','item_nbr'],
            'partitioned_store_item_data', 'store_item');
        
        expect(sql).toMatch(/MIN\(CASE WHEN date BETWEEN DATE_SUB\(DATE\('2024-01-01'\),INTERVAL 7 DAY\)/);
        expect(sql).toMatch(/AND DATE_SUB\(DATE\('2024-01-01'\),INTERVAL 1 DAY\)/);
        expect(sql).toMatch(/AND\s+unit_sales > 0 THEN\s+DATE_DIFF\(DATE\('2024-01-01'\),date,DAY\) - 1\s+ELSE NULL END/);
        expect(sql).toMatch(/AS store_item_last_sales_app_past_7_days/);
        expect(sql).toMatch(/\s+SUM\(CASE WHEN date BETWEEN/)
        expect(sql).toMatch(/DATE_SUB\(DATE\('2024-01-01'\),INTERVAL 7 DAY\)/)
        expect(sql).toMatch(/DATE_SUB\(DATE\('2024-01-01'\),INTERVAL 1 DAY\)/)
        expect(sql).toMatch(/unit_sales > 0 THEN 1 ELSE 0/)
        expect(sql).toMatch(/\s+\/ 7 AS store_item_percent_days_with_sales_last_7_days/)
    });
    
    it('generate sql script for 14-day window on onpromotion', () => {
        const sql = find_first_last('2024-01-05', 'onpromotion', [14], ['class','store_nbr'],
            'partitioned_store_class_data', 'class_store');
        expect(sql).toMatch(/MAX\(CASE WHEN date BETWEEN DATE_SUB\(DATE\('2024-01-05'\),INTERVAL 14 DAY\)/);
        expect(sql).toMatch(/DATE_SUB\(DATE\('2024-01-05'\),INTERVAL 1 DAY\)/);
        expect(sql).toMatch(/onpromotion > 0 THEN/)
        expect(sql).toMatch(/DATE_DIFF\(DATE\('2024-01-05'\),date,DAY\)/)
        expect(sql).toMatch(/AS class_store_first_promo_app_past_14_days/)
    });
});