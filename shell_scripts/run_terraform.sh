PROJECT_ID=$(gcloud config list --format "value(core.project)")
PROJECT_NBR=$(gcloud projects describe $PROJECT_ID | grep projectNumber | \
              cut -d':' -f2 | tr -d "'" | xargs)
GCP_REGION="europe-west1"
UMSA="corpor-sales-sa"

cd $(pwd)/terraform 
sed -i 's/\r$//' main.tf
terraform init

terraform plan \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" 

terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}"
  --auto-approve >> provisioning.output
