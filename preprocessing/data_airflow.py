# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 11:44:32 2025

@author: congx
"""
import os
from airflow import models
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
# from airflow.providers.google.common.hooks.base_google import GoogleBaseHook

code_bucket = "corpor-sales-scripts"
train_data_process_script = "gs://" + code_bucket + "/preprocess/train_data_process.py"
# train_data_process_script= "gs://" + code_bucket + "/preprocess/dummy_test.py"
# project_id = os.environ.get("GCP_PROJECT")     # or "GOOGLE_CLOUD_PROJECT"
# region = os.environ.get("COMPOSER_REGION")

project_id = models.Variable.get('project_id')
# umsa = models.Variable.get('UMSA_FQN')
umsa = os.environ.get('UMSA')
# subnet_nm = models.Variable.get('SUBNET_NM')
subnet_nm = os.environ.get('SUBNET_NM')
region = models.Variable.get('region')

sa_fqn = umsa + "@" + project_id + ".iam.gserviceaccount.com"
subnet = f"projects/{project_id}/regions/europe-west1/subnetworks/{subnet_nm}"

SPARK_CONFIG = {
    "spark.executor.memory": "8g",
    "spark.driver.memory": "4g",
    "spark.sql.shuffle.partitions": "100",
    "spark.sql.adaptive.enabled": "true",
    "spark.dynamicAllocation.enabled": "true",
    "spark.dynamicAllocation.minExecutors": "2",
    "spark.dynamicAllocation.initialExecutors": "4",
    "spark.dynamicAllocation.maxExecutors": "10",
    "spark.sql.adaptive.skewJoin.enabled": "true",
}


BATCH_ID = "corpor-sales-training-data-preprocess"
BATCH_CONFIG = {
    "pyspark_batch":{
        "main_python_file_uri":train_data_process_script,
        "jar_file_uris":["gs://corpor-sales-lib/libs/gcs-connector-hadoop3-latest.jar"]
        },
    "environment_config":{
        "execution_config":{
            "service_account":sa_fqn,
            "subnetwork_uri":subnet
            }
        },
    "runtime_config":{
        "version":"2.2",
        "properties":SPARK_CONFIG
        }
    }

with models.DAG(
  dag_id='corpor-sales-prediction',
  schedule_interval=None,
):
    create_batch_1 = DataprocCreateBatchOperator(
                            task_id="train_data_process",
                            project_id=project_id,
                            region=region,
                            batch=BATCH_CONFIG,
                            batch_id=BATCH_ID
                           )