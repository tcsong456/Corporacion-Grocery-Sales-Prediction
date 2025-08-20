publish("mock_original_data", { type: "table", tags:["unit_test"] }).query(ctx => `
  SELECT * FROM UNNEST([
    STRUCT(1 AS store_nbr, 10 AS item_nbr, DATE '2017-6-14' AS date, 10 AS unit_sales),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, DATE '2017-6-15' AS date, 20 AS unit_sales),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, DATE '2017-6-16' AS date, 5 AS unit_sales),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, DATE '2017-6-17' AS date, 11 AS unit_sales),
    STRUCT(1 AS store_nbr, 10 AS item_nbr, DATE '2017-6-18' AS date, 100 AS unit_sales)
  ])
`);