PROJECT_ID=$(gcloud config list --format "value(core.project)")
GCP_REGION="europe-west1"
UMSA="corpor-sales-sa"

cd $(pwd)/terraform 
terraform init

terraform plan \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}"

terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" \
  --auto-approve >> provisioning.output