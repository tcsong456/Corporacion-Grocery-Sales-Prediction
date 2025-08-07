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

terraform plan \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" \
  -var="build_id=local-run-000" 

terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" \
  -var="build_id=local-run-000" \
  --auto-approve >> provisioning.output
