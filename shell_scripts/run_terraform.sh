gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
PROJECT_ID=$(jq -r '.project_id' $GOOGLE_APPLICATION_CREDENTIALS)
gcloud config set project "$PROJECT_ID"

TEST_TABLE="df_test"
OUTPUT_DATASET="corpor_sales_submission"
OUTPUT_TABLE="corpor_preds"
INPUT_DATASET="corpor_sales_prediction_dataset"
GCP_REGION="europe-west1"
UMSA="corpor-sales-sa"
backend_bucket="tfstate-${PROJECT_ID}"
CC3_ENV_NM="${PROJECT_ID}-cc3"
SALES_BUCKT="corpor-sales-data"
TOPIC="cc3-bucket-events"
trainer_sa="corpor-lgb-trainer"
pipeline_sa="pipeline-runner"
kfp_sa="corpor-kfp-sa"

if ! gsutil ls -b gs://${backend_bucket} &>/dev/null; then
  echo "creating bucket ${backend_bucket}"
  gsutil mb -p ${PROJECT_ID} -l ${GCP_REGION} gs://${backend_bucket}
  gsutil uniformbucketlevelaccess set on gs://${backend_bucket}
else
  echo "gs://${backend_bucket} already exists"
fi
gsutil versioning set on gs://${backend_bucket}
gcloud storage buckets add-iam-policy-binding gs://$backend_bucket \
  --member="serviceAccount:$UMSA@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
gcloud storage buckets add-iam-policy-binding gs://$backend_bucket \
  --member="serviceAccount:$UMSA@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

cd $(pwd)/terraform 
sed -i 's/\r$//' main.tf 
terraform init -input=false -reconfigure -backend-config="credentials=/run/secrets/key.json"

terraform plan -input=false -no-color \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${GCP_REGION}" \
  -var="umsa=${UMSA}" \
  -var="trainer_sa=${trainer_sa}" \
  -var="pipeline_sa=${pipeline_sa}" \
  -var="kfp_sa=${kfp_sa}" \
  -var="preds_dataset=${OUTPUT_DATASET}" \
  -var="preds_table=${OUTPUT_TABLE}"

terraform apply -input=false \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${GCP_REGION}" \
  -var="umsa=${UMSA}" \
  -var="trainer_sa=${trainer_sa}" \
  -var="pipeline_sa=${pipeline_sa}" \
  -var="kfp_sa=${kfp_sa}" \
  -var="preds_dataset=${OUTPUT_DATASET}" \
  -var="preds_table=${OUTPUT_TABLE}" \
  --auto-approve >> provisioning.output

composer_bucket_prefix=$(gcloud composer environments describe ${PROJECT_ID}-cc3 \
						--location=${GCP_REGION} \
						--format="value(config.dagGcsPrefix)" \
						| sed 's#^gs://##' | cut -d'/' -f1)
echo '{"purpose":"object_finalize"}' > trigger.json
gsutil cp trigger.json gs://${composer_bucket_prefix}/dags/_trigger/trigger-$(date +%s).json


