gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
PROJECT_ID=$(jq -r '.project_id' $GOOGLE_APPLICATION_CREDENTIALS)
gcloud config set project "$PROJECT_ID"

GCP_REGION="europe-west1"
UMSA="corpor-sales-sa"
backend_bucket="tfstate-${PROJECT_ID}"

if ! gsutil -b gs://${backend_bucket} &>/dev/null; then
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
terraform init -input=false -backend-config="credentials=/run/secrets/key.json"
if gcloud eventarc triggers describe "trigger-after-all-dags-done" \
  --location=${GCP_REGION} --project=${PROJECT_ID} >/dev/null 2>&1; then
  echo "Found remote trigger on GCP"
  terraform import google_eventarc_trigger.dataform_on_airflow_completion \
    projects/${PROJECT_ID}/locations/${GCP_REGION}/trigger-after-all-dags-done
else
  echo "Remote trigger not found,import skipped"
fi

terraform plan \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" \
  -var="build_id=local-run-006"

terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" \
  -var="build_id=local-run-006" \
  --auto-approve >> provisioning.output
