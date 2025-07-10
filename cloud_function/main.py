from google.auth import default
from googleapiclient import discovery
import base64,os,json

project_id = os.environ['PROJECT_ID']
region     = os.environ['REGION']
composer_env = os.environ['COMPOSER_ENV']
dag_id     = os.environ['DAG_ID']

creds,_ = default()
composer = discovery.build("composer","v1",credentials=creds,cache_discovery=False)

def handler(event,context):
    print(f"RAW EVENT: {event}")
    data = event.get("data")
    if not data:
        print("No data in payload,exit the program")
        return
    
    message = json.loads(base64.b64decode(data).decode())
    name = message.get('name','')
    print(f'uploaded file:{name} detected')
    
    if 'data_airflow.py' not in name:
        raise ValueError(f'file:{name} detected,but expect airflow.py in the dag file')
    
    try:
        resource_fqn = f"projects/{project_id}/locations/{region}/environments/{composer_env}"
        body = {'dagId':dag_id,
                'dagRunId':f'dag-upload-{context.event_id}'}
        response = composer.projects().locations().environments().run(body=body,
                                                                      name=resource_fqn).execute()
        print(f"DAG run triggered successfully: {response}")
    except Exception as e:
        print(f"Failed to trigger DAG run: {e}")
        raise