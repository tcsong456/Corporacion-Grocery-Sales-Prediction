import os
import datetime
import tempfile
from kfp import compiler
from google.cloud import aiplatform
from fastapi import FastAPI, Request, Response
from hpt_and_train import hpt_train_pipeline

PROJECT = os.environ['project_id']
REGION = os.environ['region']
PIPELINE_ROOT = os.environ['pipeline_root']
PIPELINE_SA = os.environ['pipeline_sa']
METRIC_TAG = os.environ['metric_tag']
MAX_TRIALS = int(os.environ.get('max_trials',"50"))
PARALLEL_TRIALS = int(os.environ.get('parallel_trials',"4"))
TRAINER_SA = os.environ['trainer_sa']
HPT_GCS_ROOT = os.environ['hpt_gcs_root']

app = FastAPI()

def _compile_to_temp():
    tmp = tempfile.NamedTemporaryFile(suffix='.json',delete=False)
    compiler.Compiler().compile(
        pipeline_func=hpt_train_pipeline,
        package_path=tmp.name
      )
    return tmp.name

def _submit(params):
    aiplatform.init(project=PROJECT, location=REGION)
    temp_path = _compile_to_temp()
    job = aiplatform.PipelineJob(
        display_name=f"corpor-sales-lgb-training-{datetime.datetime.utcnow():%Y%m%d-%H%M%S}",
        template_path=temp_path,
        pipeline_root=PIPELINE_ROOT,
        parameter_values=params
      )
    job.run(service_account=PIPELINE_SA,
            sync=False)

@app.post('/')
async def receive_eventarc_request(request: Request):
    body = {}
    try:
        body = await request.json()
        print(f'request body: {body}')
    except Exception as e:
        print(f'Encountering error:{e},fail to receive the request')
        exit(1)
        
    params = {
        "project": PROJECT,
        "region": REGION,
        "metric_tag": body.get("metric_tag", METRIC_TAG),
        "max_trials": int(body.get("max_trials", MAX_TRIALS)),
        "parallel_trials": int(body.get("parallel_trials", PARALLEL_TRIALS)),
        "service_account": body.get("service_account", TRAINER_SA),
        "hpt_gcs_root": body.get("hpt_gcs_root", HPT_GCS_ROOT)
      }
    _submit(params)
    
    return Response(status_code=204)