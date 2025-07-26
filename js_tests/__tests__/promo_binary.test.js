const { promo_indicator_pivot } = require("../../corpor_sales_dataform/includes/promo_indicators")

describe('test promo_indicator_pivot sql generation', () => {
    it('generate sql script for class,store_nbr future 16 days of onpromotion', () => {
        const sql =  promo_indicator_pivot('2017-6-14',['class','store_nbr'],'partitioned_class_store_data','class_store');
        expect(sql).toMatch(/MAX\(CASE WHEN date=DATE\('2017-06-14'\) THEN onpromotion ELSE NULL END\)/);
        expect(sql).toMatch(/AS class_store_promo_0/);
        expect(sql).toMatch(/MAX\(CASE WHEN date=DATE\('2017-06-29'\) THEN onpromotion ELSE NULL END\)/);
        expect(sql).toMatch(/AS class_store_promo_15/);
        expect(sql).toMatch(/WHERE date BETWEEN DATE\('2017-06-14'\) AND DATE\('2017-06-29'\)\s+GROUP BY class,store_nbr/);
    });
    
    it('generate sql script for store_nbr,item_nbr future 16 days of onpromotion', () => {
        const sql =  promo_indicator_pivot('2017-6-21',['store_nbr','item_nbr'],'partitioned_store_item_data','store_item');
        expect(sql).toMatch(/MAX\(CASE WHEN date=DATE\('2017-06-25'\) THEN onpromotion ELSE NULL END\)/);
        expect(sql).toMatch(/AS store_item_promo_4/)
        expect(sql).toMatch(/FROM\s+partitioned_store_item_data/)
    });
});