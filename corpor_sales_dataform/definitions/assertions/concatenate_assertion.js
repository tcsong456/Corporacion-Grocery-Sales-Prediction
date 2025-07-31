const dates = ['2017-6-14','2017-6-21','2017-6-28'];

const assert_concatenate_row_counts = 
assert('assert_concatenate_row_counts', { tags: ["concatenate_test"] }).query(ctx => `
  WITH part AS (
  ${dates.map((date,i) => `
    ${i > 0 ? "UNION ALL\n": ''}SELECT COUNT(*) AS c FROM ${ctx.ref(`mock_merge_features_${date.replace(/-/g,'')}`)}
    `).join('\n')}
  ),
  expected_rows AS (SELECT SUM(c) AS row_counts FROM part),
  actual_rows AS (SELECT COUNT(*) AS row_counts FROM ${ctx.ref("expected_concate_models")})
  SELECT 'mismatch_rowcounts' AS issue, expected_rows.row_counts AS expected_rowcounts, 
  actual_rows.row_counts AS actual_rowcounts
  FROM expected_rows,actual_rows
  WHERE expected_rows.row_counts <> actual_rows.row_counts
  `);

module.exports = { assert_concatenate_row_counts };