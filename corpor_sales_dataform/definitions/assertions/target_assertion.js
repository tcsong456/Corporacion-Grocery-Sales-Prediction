const target_assertion = 
assert("assert_target_2017614", { tags: ["unit_test"] }).query(ctx => `
  WITH actual_dataset AS (SELECT * FROM ${ctx.ref("actual_target_data")}),
       expected_dastaset AS (SELECT * FROM ${ctx.ref("expected_target_data")})
  (
  SELECT 'extra' AS missing_rows, TO_JSON_STRING((SELECT AS STRUCT a.*)) AS row_json
  FROM actual_dataset a
  EXCEPT DISTINCT
  SELECT 'extra', TO_JSON_STRING((SELECT AS STRUCT e.*)) AS row_json FROM  expected_dastaset e
  )
  UNION ALL
  (
  SELECT 'missing' AS diff_rows, TO_JSON_STRING((SELECT AS STRUCT e.*)) AS row_json
  FROM expected_dastaset e
  EXCEPT DISTINCT
  SELECT 'missing', TO_JSON_STRING((SELECT AS STRUCT a.*)) AS row_json FROM actual_dataset a
  )
`);

module.exports = { target_assertion };