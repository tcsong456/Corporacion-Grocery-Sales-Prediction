#!/bin/bash

#cd dataform
#dataform run

#cd ..
PROJECT_NAME="corporacion-sales-prediction"
gcloud auth activate-service-account --key-file=key.json
project_id=$(gcloud projects list --format="value(projectId)" --filter="name:$PROJECT_NAME")
gcloud config set project $project_id

dataset_id=$(bq ls --project_id=$project_id --format=json | jq -r '.[].datasetReference.datasetId')
tables=$(bq ls --max_results=1000 --format=json ${project_id}:${dataset_id} | jq -r '.[].tableReference.tableId')
echo "$project_id,$dataset_id,$table_id"

keeps=('partitioned_class_store_data'
       'partitioned_item_data'
       'partitioned_store_item_data'
       'y_train'
       'y_valid'
       'df_train'
       'df_valid'
       'df_test')

for tbl in $tables;do
  if [[ ! " ${keeps[@]} " =~ " $tbl "  ]];then
     echo "deleting $tbl..."
     bq rm -f -t ${project_id}:${dataset_id}.$tbl
  fi
done
