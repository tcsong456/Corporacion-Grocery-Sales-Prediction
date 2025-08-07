gcloud auth activate-service-account --key-file=key.json
PROJECT_NAME=$1
PROJECT_ID=$(gcloud projects list --filter="name:${PROJECT_NAME}" --format="value(projectId)")
gcloud config set project $PROJECT_ID
#export GOOGLE_APPLICATION_CREDENTIALS=key.json
#gcloud auth application-default set-quota-project $PROJECT_ID
#PROJECT_NBR=`gcloud projects describe $PROJECT_ID | grep projectNumber | \
#cut -d':' -f2 |  tr -d "'" | xargs`
SA_NAME="corpor-sales-sa"
#gcloud iam service-accounts list --project=$PROJECT_ID --format="value(email)" | \
#grep -q "${SA_NAME}@$PROJECT_ID.iam.gserviceaccount.com" || \
#gcloud iam service-accounts create $SA_NAME \
#                                   --project=$PROJECT_ID \
#                                   --display-name="corpor sales service account"
  
ROLES=("roles/editor"
       "roles/iam.serviceAccountUser"
       "roles/storage.admin"
       "roles/resourcemanager.projectIamAdmin"
)
for ROLE in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
           --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
           --role="$ROLE"
done

#SA_KEY_FILE='key.json'
#[ -f $SA_KEY_FILE ] || \
#gcloud iam service-accounts keys create $SA_KEY_FILE \
#  --project=$PROJECT_ID \
#  --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com
