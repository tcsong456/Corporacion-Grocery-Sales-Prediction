const { rolling_window_stats } =  require("../../corpor_sales_dataform/includes/sales_window_stats")

describe('test sql generation for rolling sales stats', () => {
    it('sql script for store_item window size of 30', () => {
        const sql = rolling_window_stats('2017-6-14',[30],0.9,['store_nbr','item_nbr'],
            'partitioned_store_item_data','store_item');
        expect(sql).toMatch(/MIN\(unit_sales\) AS unit_sales_min/);
        expect(sql).toMatch(/AVG\(unit_sales\) AS unit_sales_mean/);
        expect(sql).toMatch(/APPROX_QUANTILES\(unit_sales,2\)\[OFFSET\(1\)\] AS unit_sales_median/);
        expect(sql).toMatch(/SUM\(unit_sales \*\s+POWER\(0.9,DATE_DIFF\(DATE\('2017-6-14'\),date,DAY\)-1\)\)/);
        expect(sql).toMatch(/30 AS source/);
        expect(sql).toMatch(/FROM partitioned_store_item_data/);
        expect(sql).toMatch(/DATE_SUB\(DATE\('2017-6-14'\),INTERVAL 30 DAY\)/);
        expect(sql).toMatch(/DATE_SUB\(DATE\('2017-6-14'\),INTERVAL 1 DAY/);
        expect(sql).toMatch(/MAX\(CASE WHEN source=30 THEN unit_sales_median END\) AS store_item_unit_sales_median_30/);
        expect(sql).toMatch(/MAX\(CASE WHEN source=30 THEN unit_sales_decay_sum END\) AS store_item_unit_sales_decay_sum_30/);
    });
    
    it('sql scrip for class_store window size of 14', () => {
        const sql = rolling_window_stats('2017-6-14',[14],0.9,['class','store_nbr'],
            'partitioned_class_store_data','class_store');
        expect(sql).toMatch(/MAX\(unit_sales\) AS unit_sales_max/);
        expect(sql).toMatch(/STDDEV_SAMP\(unit_sales\) AS unit_sales_std/);
        expect(sql).toMatch(/14 AS source/);
        expect(sql).toMatch(/FROM partitioned_class_store_data/);
        expect(sql).toMatch(/MAX\(CASE WHEN source=14 THEN unit_sales_max END\) AS class_store_unit_sales_max_14/);
        expect(sql).toMatch(/MAX\(CASE WHEN source=14 THEN unit_sales_std END\) AS class_store_unit_sales_std_14/);
    });
});