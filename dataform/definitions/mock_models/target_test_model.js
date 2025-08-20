const { generateDates } = require("includes/target_extractor");

publish("actual_target_data", { type: "view", tags: ["unit_test"] }).query(ctx => 
  generateDates(
    '2017-6-14',
    5,
    ctx,
    'mock_original_data'
  )
);

publish("expected_target_data", { type: "view", tags: ["unit_test"] }).query(cty =>`
  SELECT * FROM UNNEST([
    STRUCT(1 AS store_nbr, 10 AS item_nbr, 10 AS y0, NULL AS y1, NULL AS y2, NULL AS y3, 100 AS y4),
    STRUCT(2 AS store_nbr, 20 AS item_nbr, NULL AS y0, 20 AS y1, NULL AS y2, 11 AS y3, NULL AS y4),
    STRUCT(3 AS store_nbr, 30 AS item_nbr, NULL AS y0, NULL AS y1, 5 AS y2, NULL AS y3, NULL AS y4)
  ])
`);