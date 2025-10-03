import os
from kfp import dsl, compiler
from google.cloud import aiplatform
from google_cloud_pipeline_components.v1.hyperparameter_tuning_job import HyperparameterTuningJobRunOp
from google_cloud_pipeline_components.v1 import hyperparameter_tuning_job as hpt_job
from google.cloud.aiplatform import hyperparameter_tuning as hpt
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google_cloud_pipeline_components.types import artifact_types

@dsl.component(
  base_image="python:3.10",
  packages_to_install=[
    "kfp==2.4.0",
    "kfp-pipeline-spec==0.2.2",
    "kfp-server-api>=2.0.0,<2.1.0",
    "click>=8,<9",
    "kubernetes>=8,<27",
    "PyYAML>=5.3,<7",
    "requests-toolbelt>=0.8,<1",
    "tabulate>=0.8.6,<1",
    "protobuf<4",
    "urllib3<2",
    "google-cloud-aiplatform==1.64.0",
    "google-cloud-storage>=2.14.0",
    ]
)
def get_best_param_from_hpt(
   gcp_resources: str,
   project: str,
   location: str,
   metric_id: str = "rmse",
   goal: str = 'minimize'
    ) -> str:
    import json
    from google.cloud.aiplatform_v1 import JobServiceClient
    
    if not gcp_resources:
        raise ValueError("gcp_resources is empty")
    
    try:
        res = json.loads(gcp_resources)
        uri = res['resources'][0]['resourceUri']
    except Exception as e:
        raise ValueError(f"Unexpected gcp_resources error: {e}; value={gcp_resources!r}")
        
    if uri.startswith("https://"):
        if "/projects/" not in uri:
            raise ValueError(f"Unexpected URI (no /projects/): {uri!r}")
        job_name = "projects/" + uri.split("/projects/", 1)[1]
    elif uri.startswith("projects/"):
        job_name = uri
    else:
        raise ValueError(f"Unexpected resource ref: {uri!r}")

    parts = job_name.split("/")
    region = parts[parts.index("locations") + 1]
    client = JobServiceClient(client_options={'api_endpoint': f"{region}-aiplatform.googleapis.com"})
    job = client.get_hyperparameter_tuning_job(name=job_name)
    
    def metric_value(measurement, metric_id):
        if measurement is None:
            return None
        for m in measurement.metrics:
            if m.metric_id == metric_id:
                return m.value
        return None
    
    best_trial = None
    for trial in job.trials:
        if trial.final_measurement is None:
            continue
        if best_trial is None:
            best_trial = trial
            continue
          
        cur_metric = metric_value(trial.final_measurement, metric_id)
        best_metric = metric_value(best_trial.final_measurement, metric_id)
        if cur_metric is None and best_metric is None:
            continue
        if (goal == 'minimize' and cur_metric < best_metric) or (goal == 'maximize'  and cur_metric > best_metric):
            best_trial = trial
    
    if best_trial is None:
        raise RuntimeError("No completed trials with final_measurement found.")
        
    params = {}
    for p in best_trial.parameters:
        pid = p.parameter_id
        if hasattr(p, "double_value") and p.HasField("double_value"):
            params[pid] = p.double_value
        elif hasattr(p, "integer_value") and p.HasField("integer_value"):
            params[pid] = p.integer_value
        elif hasattr(p, "string_value") and p.HasField("string_value"):
            params[pid] = p.string_value
        else:
            params[pid] = None
    return json.dumps(params)

@dsl.component(
  base_image="python:3.10-slim",
  packages_to_install=[
      "kfp==2.6.0",
      "kfp-pipeline-spec==0.3.0",
      "kfp-server-api>=2.0.0,<2.1.0",
      "click==8.1.7",
      "kubernetes<27",
      "PyYAML<7",
      "requests-toolbelt<1",
      "tabulate<1",
      "protobuf==4.25.3",
      "urllib3==1.26.18",
      "google-cloud-aiplatform==1.64.0",
      "google-cloud-storage>=2.14.0",])
def deploy_vertex_endpoint(
    project: str,
    region: str,
    model_id: str,
    display_name: str,
    min_replica_count: int,
    max_replica_count: int
    ) -> str:
    from google.cloud import aiplatform
    aiplatform.init(project=project, location=region)
    
    endpoints = aiplatform.Endpoint.list(filter=f'display_name={display_name}')
    if endpoints:
        endpoint = endpoints[0]
    else:
        endpoint = aiplatform.Endpoint.create(display_name=display_name)
    
    model = aiplatform.Model(model_name=f"projects/{project}/locations/{region}/models/{model_id}")
    
    endpoint.deploy(
      model=model,
      deployed_model_display_name="corpor-sales-lightgbm-v1",
      machine_type='n1-highmem-8',
      min_replica_count=min_replica_count,
      max_replica_count=max_replica_count
      )
    
    return endpoint.resource_name

@dsl.component(
  base_image="python:3.10-slim"
  )
def get_model_id(model: dsl.Input[dsl.Artifact]) -> str:
    rn = model.metadata['resourceName']
    model_name = rn.split('@')[0]
    model_id = model_name.rsplit('/', 1)[-1]
    return model_id

@dsl.pipeline(name="hpt-and-train-pipeline")
def hpt_train_pipeline(
    project: str,
    region: str,
    metric_tag: str,
    max_trials: int,
    parallel_trials: int,
    service_account: str,
    hpt_gcs_root: str
    ):
    TRAINER_IMAGE = os.environ['trainer_image']
    SERVING_IMAGE = os.environ['serving_image']
    PREDICT_IMAGE = os.environ['predict_image']
    worker_pool_spec= [
        {"name": "bq_project", "value": "corporacion-sales-forecasting"},
        {"name": "bq_dataset", "value": "corpor_sales_prediction_dataset"},
        {"name": "train_table", "value": "merge_features"},
        {"name": "valid_table", "value": "df_valid"},
        {"name": "label_train", "value": "y"},
        {"name": "label_val", "value": "y_valid"},
        {"name": "items_table", "value": "item_data_table"},
        {"name": "metric", "value": "rmse"},
        ]
    worker_pool_specs = [{
      "machine_spec": {"machine_type": 'n1-highmem-8'},
      "replica_count": 1,
      "container_spec": {
        "image_uri": TRAINER_IMAGE,
        "env": worker_pool_spec,
        "args": [
              "--mode", "hpt",
              "--early_stopping_rounds", "50",
          ]
        }
      }]
    
    hptjob = HyperparameterTuningJobRunOp(
      display_name='lightgbm-hpt',
      project=project,
      location=region,
      max_trial_count=max_trials,
      parallel_trial_count=parallel_trials,
      study_spec_metrics=hpt_job.serialize_metrics({"rmse": "minimize"}),
      study_spec_parameters=hpt_job.serialize_parameters({
          "learning_rate": hpt.DoubleParameterSpec(min=1e-3, max=1e-1, scale='log'),
          "num_leaves": hpt.IntegerParameterSpec(min=40, max=120, scale='linear'),
          "feature_fraction": hpt.DoubleParameterSpec(min=0.4, max=1.0, scale='linear'),
          "bagging_fraction": hpt.DoubleParameterSpec(min=0.4, max=1.0, scale='linear'),
          "bagging_freq": hpt.IntegerParameterSpec(min=1, max=10, scale='linear'),
          "min_data_in_leaf": hpt.IntegerParameterSpec(min=50, max=350, scale='linear')
          }),
      worker_pool_specs=worker_pool_specs,
      service_account=service_account,
      base_output_directory=hpt_gcs_root
      )
    
    best_param_json = get_best_param_from_hpt(
      gcp_resources=hptjob.outputs['gcp_resources'],
      project=project,
      location=region,
      metric_id=metric_tag,
      goal='minimize'
      )
    
    train_worker_pool = [{
      "machine_spec": {"machine_type": "n1-highmem-8"},
      "replica_count": 1,
      "container_spec": {
        "image_uri": TRAINER_IMAGE,
        "env": worker_pool_spec,
        "args": [
          "--mode", "final",
          "--best_params_json", f"{best_param_json}"
          ]
        }
      }]
    
    lgb_train_job = CustomTrainingJobOp(
        display_name="lightgbm-final-train",
        project=project,
        location=region,
        worker_pool_specs=train_worker_pool,
        service_account=service_account,
        base_output_directory=hpt_gcs_root
      )
    lgb_train_job.after(best_param_json)
    
    unmanaged = dsl.importer(
        artifact_class=artifact_types.UnmanagedContainerModel,
        artifact_uri="gs://corpor-sales-lgb-hpt/final/",
        metadata={"containerSpec": {
          "imageUri": SERVING_IMAGE,
          "predictRoute": "/predict",
          "healthRoute": "/health"
            }
          }
      )
    unmanaged.after(lgb_train_job)
    
    upload = ModelUploadOp(
        project=project,
        location=region,
        display_name="corpor-sales-lightgbm",
        unmanaged_container_model=unmanaged.outputs["artifact"],
        labels={'pipeline': 'corpor-sales', 'stage': 'final-training'}
      )
    upload.after(unmanaged)
    
    model_id = get_model_id(model=upload.outputs['model'])
    
    deploy_vertex_endpoint(
      project=project,
      region=region,
      model_id=model_id.output,
      display_name='corpor-sales-trained-lightgbm',
      min_replica_count=1,
      max_replica_count=3
      )
    
    pred_worker_pool = [
        {
          "machine_spec": {"machine_type": "n1-highmem-8"},
          "replica_count": 1,
          "container_spec": {
              "image_uri": PREDICT_IMAGE,
              "env": [
                  {"name": "PROJECT_ID", "value": "corporacion-sales-forecasting"},
                  {"name": "MODEL_URI", "value": "gs://corpor-sales-lgb-hpt/final"},
                  {"name": "SRC_TABLE", "value": "corporacion-sales-forecasting.corpor_sales_prediction_dataset.df_test"},
                  {"name": "DST_TABLE", "value": "corporacion-sales-forecasting.corpor_sales_submission.corpor_preds"},
                  {"name": "REGION", "value": "europe-west1"}
                ]
            }
          }
      ]
    
    prediction_job = CustomTrainingJobOp(
        display_name="lightgbm-prediction",
        project=project,
        location=region,
        worker_pool_specs=pred_worker_pool,
        service_account=service_account
      )
    prediction_job.after(upload)
    
    lgb_train_job.set_caching_options(False)
    upload.set_caching_options(False)
    prediction_job.set_caching_options(False)
    
# if __name__ == '__main__':
#     PROJECT = os.environ.get('PROJECT_ID')
#     REGION  = os.environ.get('region')
#     TRAINER_SA = os.environ.get('trainer_sa')
#     PIPELINE_SA = os.environ.get('pipeline_sa')
#     PIPELINE_ROOT = os.environ.get('pipeline_root')
#     HPT_GCS_ROOT = os.environ.get('hpt_gcs_root')
#     required_evs = {
#         "PROJECT_ID": PROJECT,
#         "LOCATION": REGION,
#         "TRAINER_SA": TRAINER_SA,
#         "PIPELINE_SA": PIPELINE_SA,
#         'PIPELINE_ROOT': PIPELINE_ROOT,
#         'HPT_GCS_ROOT': HPT_GCS_ROOT
#       }
#     missing_reqs = [k for k,v in required_evs.items() if not v]
#     if missing_reqs:
#         raise RuntimeError(f"missing required parameterL: {', '.join(missing_reqs)}")
        
    
#     BQ_DATASET = 'corpor_sales_prediction_dataset'
#     TRAIN_TABLE = 'df_train'
#     VALID_TABLE = 'df_valid'
#     TRAIN_LABEL = 'y_train'
#     VALID_LABEL = 'y_valid'
#     ITEMS_TABLE = 'item_data_table'
#     METRIC_TAG = 'rmse'
#     MAX_TRIALS = 3
#     PARALLEL_TRIALS = 3
#     PACKAGE_PATH = 'lightgbm_final_pipeline.json'
#     TRAINER_SERVICE_ACCOUNT=f"{TRAINER_SA}@{PROJECT}.iam.gserviceaccount.com"
#     PIPELINE_SERVICE_ACCOUNT=f"{PIPELINE_SA}@{PROJECT}.iam.gserviceaccount.com"
    
#     compiler.Compiler().compile(
#       pipeline_func=hpt_train_pipeline,
#       package_path=PACKAGE_PATH
#       )
#     aiplatform.init(project=PROJECT, location=REGION)
#     job = aiplatform.PipelineJob(
#       display_name='lgb-final-training',
#       template_path=PACKAGE_PATH,
#       pipeline_root=PIPELINE_ROOT,
#       parameter_values={
#           'project':PROJECT,
#           'region':REGION,
#           'metric_tag':METRIC_TAG,
#           'max_trials':MAX_TRIALS,
#           'parallel_trials':PARALLEL_TRIALS,
#           'service_account':TRAINER_SERVICE_ACCOUNT,
#           'hpt_gcs_root': HPT_GCS_ROOT
#         }
#       )
#     job.run(service_account=PIPELINE_SERVICE_ACCOUNT,
#             sync=True)
  
#%%

  