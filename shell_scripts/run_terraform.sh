gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
PROJECT_ID=$(jq -r '.project_id' $GOOGLE_APPLICATION_CREDENTIALS)
gcloud config set project "$PROJECT_ID"

GCP_REGION="europe-west1"
UMSA="corpor-sales-sa"
backend_bucket="tfstate-${PROJECT_ID}"
CC3_ENV_NM="${PROJECT_ID}-cc3"
SALES_BUCKT="corpor-sales-data"
TOPIC="cc3-bucket-events"

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

terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="umsa=${UMSA}" \
  -var="region=${GCP_REGION}" \
  --auto-approve >> provisioning.output

gcloud storage rsync -r --checksums-only ../data "gs://$SALES_BUCKT/"
TRIGGER_NAME=$(
  gcloud eventarc triggers list \
    --location "$GCP_REGION" \
    --filter="transport.pubsub.topic~$TOPIC" \
    --format='value(name)'
  )
for i in {1..90}; do
  sub="$(gcloud eventarc triggers describe "$TRIGGER_NAME" \
          --location "$GCP_REGION" \
          --format='value(transport.pubsub.subscription)')"
  if [[ -n "$sub" ]]; then
    echo "Trigger ready: $sub"
    break
  fi
  sleep 2
done
[[ -n "$sub" ]] || { echo "Eventarc trigger not ACTIVE"; exit 1; }

DAG_PREFIX=$(gcloud composer environments describe "$CC3_ENV_NM" --location "$GCP_REGION" --format='value(config.dagGcsPrefix)')
DATA_BUCKET=$(echo "$DAG_PREFIX" | sed -e 's#^gs://##' -e 's#/.*$##')
printf '{"ts":"%s"}\n' "$(date -Iseconds)" > run.json
gcloud storage cp run.json "gs://$DATA_BUCKET/dags/_trigger/run.json"
