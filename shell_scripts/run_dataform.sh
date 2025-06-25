dataform_folder="corpor_sales_dataform"
PROJECT_ID=$(jq -r '.project_id' ./key.json)
gcloud auth activate-service-account --key-file=./key.json
gcloud config set project "$PROJECT_ID"
bq_dt_nm=$(bq ls --format=json | jq -r '.[].datasetReference.datasetId')
[ -d $dataform_folder ] || dataform init $dataform_folder \
                                      --default-database=$PROJECT_ID \
                                      --default-location=europe-west1
#echo "defaultSchema: $bq_dt_nm" >> $dataform_folder/workflow_settings.yaml
cd $dataform_folder
ln -sf ../key.json .df-credentials.json
cat <<'EOF' > definitions/sales_data_creation.sqlx
config { type: "operations" }

CREATE OR REPLACE EXTERNAL TABLE `corporacion-sales-prediction.corpor_sales_prediction_dataset.raw_unit_sales`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://your-gcs-bucket/path/to/*.parquet']
);
EOF

dos2unix definitions/sales_data_creation.sqlx
dataform run --actions sales_data_creation