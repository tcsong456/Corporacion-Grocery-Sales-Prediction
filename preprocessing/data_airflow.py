# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 11:44:32 2025

@author: congx
"""
import os
from google.cloud import compute_v1
from google.api_core import exceptions
from datetime import timedelta
from airflow import models
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator

code_bucket = "corpor-sales-scripts"
train_data_process_script = "gs://" + code_bucket + "/preprocess/train_data_process.py"
train_test_concat_script = "gs://" + code_bucket + "/preprocess/train_test_concat.py"
missing_values_fill_script = "gs://" + code_bucket + "/preprocess/missing_values_fill.py"
store_item_merge_script = "gs://" + code_bucket + "/preprocess/merge_store_item.py"

project_id = os.environ.get("GCP_PROJECT_ID")     # or "GOOGLE_CLOUD_PROJECT"
region = os.environ.get("GCP_REGION")

# project_id = models.Variable.get('GCP_PROJECT_ID')
# umsa = models.Variable.get('UMSA_FQN')
umsa = os.environ.get('UMSA')
# subnet_nm = models.Variable.get('SUBNET_NM')
subnet_nm = os.environ.get('SUBNET_NM')
# region = models.Variable.get('GCP_REGION')

sa_fqn = umsa + "@" + project_id + ".iam.gserviceaccount.com"
subnet = f"projects/{project_id}/regions/europe-west1/subnetworks/{subnet_nm}"
SPARK_CONFIG = {
    "spark.executor.memory": "4g",
    "spark.driver.memory": "4g",
    "spark.sql.shuffle.partitions": "100",
    "spark.sql.adaptive.enabled": "true",
    "spark.dynamicAllocation.enabled": "true",
    "spark.dynamicAllocation.minExecutors": "2",
    "spark.dynamicAllocation.initialExecutors": "4",
    "spark.dynamicAllocation.maxExecutors": "6",
    "spark.executor.cores": "4",
    "spark.sql.adaptive.skewJoin.enabled": "true",
        }

# BATCH_ID = "corpor-sales-training-data-preprocess"
BATCH_CONFIG1 = {
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

BATCH_CONFIG2 = {
    "pyspark_batch":{
        "main_python_file_uri":train_test_concat_script,
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

BATCH_CONFIG3 = {
    "pyspark_batch":{
        "main_python_file_uri":missing_values_fill_script,
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

BATCH_CONFIG4 = {
    "pyspark_batch":{
        "main_python_file_uri":store_item_merge_script,
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

# def quota_check():
#     client = compute_v1.ProjectsClient()
#     metric = "CPUS"
#     minimal_required_cpus = 12
#     quota = client.get_region_quota(project=project_id,region=region,metric=metric)
#     available_quotas = quota.limit - quota.usage
#     if available_quotas < minimal_required_cpus:
#         raise exceptions.ResourceExhausted(f'Insufficent quota: available-{available_quotas} quotas \
#                                              required-{minimal_required_cpus} quotas')

# check_quota_availbility = PythonOperator(
#                                           task_id='check_quota',
#                                           python_callable=quota_check,
#                                           retries=3,
#                                           retry_delay=timedelta(minutes=4)
#                                             )
import time

def wait():
    time.sleep(200)


with models.DAG(
  dag_id='corpor-sales-prediction',
  schedule_interval=None,
):
    # create_batch_1 = DataprocCreateBatchOperator(
    #                         task_id="train_data_process",
    #                         project_id=project_id,
    #                         region=region,
    #                         batch=BATCH_CONFIG1,
    #                         batch_id='train-data-process-batch'
    #                         )
    
    # wait_for_quota_release_1 = PythonOperator(
    #                                         task_id='wait_for_batch1_release_quotas',
    #                                         python_callable=wait,
    #                                         )
    
    # create_batch_2 = DataprocCreateBatchOperator(
    #                         task_id="train_test_concat",
    #                         project_id=project_id,
    #                         region=region,
    #                         batch=BATCH_CONFIG2,
    #                         batch_id='train-test-concat-batch',
    #                        )
    
    # wait_for_quota_release_2 = PythonOperator(
    #                                         task_id='wait_for_batch2_release_quotas',
    #                                         python_callable=wait,
    #                                         )
    
    # create_batch_3 = DataprocCreateBatchOperator(
    #                         task_id="missing_values_fill",
    #                         project_id=project_id,
    #                         region=region,
    #                         batch=BATCH_CONFIG3,
    #                         batch_id='missing-values-fill-batch',
    #                         )
    
    # wait_for_quota_release_3 = PythonOperator(
    #                                         task_id='wait_for_batch3_release_quotas',
    #                                         python_callable=wait,
    #                                         )
    
    create_batch_4 = DataprocCreateBatchOperator(
                            task_id="store_item_merge",
                            project_id=project_id,
                            region=region,
                            batch=BATCH_CONFIG4,
                            batch_id='store-item-merge-batch'
                            )
    
    
    # create_batch_1 >> wait_for_quota_release_1 >> create_batch_2
    # create_batch_2 >> wait_for_quota_release_2 >> create_batch_3
    # create_batch_3 >> wait_for_quota_release_3 >> create_batch_4