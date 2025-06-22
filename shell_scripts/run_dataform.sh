# -*- coding: utf-8 -*-
dataform_folder="corpor_sales_dataform"
PROJECT_ID=$(jq -r '.project_id' ./key.json)
gcloud auth activate-service-account --key-file=./key.json
gcloud config set project "$PROJECT_ID"
bq_dt_nm=$(bq ls --format=json | jq -r '.[].datasetReference.datasetId')
dataform init $dataform_folder \
  --default-database=$PROJECT_ID \
  --default-location=europe-west1
cat > "$dataform_folder/dataform.json" <<EOF
  {
    "warehouse":"bigquery",
    "defaultSchema":"$bq_dt_nm",
    "defaultDadabase":"$PROJECT_ID",
    "defaultLocation":"europe-west1",
    "assertionSchema":"dataform_assertions"
      }
EOF
