const assert_merge_feature_2017614 = 
assert("assert_merge_feature_2017614", { tags: ["merge_test"] }).query(ctx => `
  WITH actual_dataset AS (SELECT * FROM ${ctx.ref("merge_features_2017614_test_model")}),
       expected_dataset AS (SELECT * FROM ${ctx.ref("expected_merge_results")})
  
  (
  SELECT 'extra' AS diff_row, TO_JSON_STRING((SELECT AS STRUCT a.*)) AS row_json
  FROM actual_dataset a
  EXCEPT DISTINCT
  SELECT 'extra', TO_JSON_STRING((SELECT AS STRUCT e.*)) AS row_json FROM expected_dataset e
  )
  UNION ALL
  (
  SELECT 'missing' AS diff_row, TO_JSON_STRING((SELECT AS STRUCT e.*)) AS row_json
  FROM expected_dataset e
  EXCEPT DISTINCT
  SELECT 'missing', TO_JSON_STRING((SELECT AS STRUCT a.*)) AS row_json FROM actual_dataset a
  )
`);

module.exports = { assert_merge_feature_2017614 };