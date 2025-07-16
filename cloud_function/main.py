import os
import base64
import json
import time
import requests
from google.auth.transport.requests import Request
from google.auth import default
from googleapiclient.discovery import build

PROJECT_ID = os.environ["PROJECT_ID"]
REGION = os.environ["REGION"]
COMPOSER_ENV = os.environ["COMPOSER_ENV"]
DAG_ID = os.environ["DAG_ID"]

creds, _ = default()
composer = build("composer", "v1", credentials=creds, cache_discovery=False)

def get_airflow_uri():
    env_name = f"projects/{PROJECT_ID}/locations/{REGION}/environments/{COMPOSER_ENV}"
    env = composer.projects().locations().environments().get(name=env_name).execute()
    return env["config"]["airflowUri"]

def wait_until_dag_ready(airflow_uri,dag_id,headers,timeout=120,interval=10):
    url = f"{airflow_uri}/api/v1/dags"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url,headers=headers)
            if resp.status_code == 200:
                dag_ids = [d["dag_id"] for d in resp.json().get("dags",[])]
                if dag_id in dag_ids:
                    print(f"{dag_id} is now available")
                    return
            else:
                print(f"warning:retuned api code:{resp.statsu_code}")
        except Exception as e:
            print(f"Error polling dag list: {e}")
        time.sleep(interval)

def trigger_dag_run(dag_id, run_id, conf=None):
    airflow_uri = get_airflow_uri()

    credentials, _ = default()
    credentials.refresh(Request())
    token = credentials.token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    wait_until_dag_ready(airflow_uri,dag_id,headers)
    
    url = f"{airflow_uri}/api/v1/dags/{dag_id}/dagRuns"
    payload = {
        "dag_run_id": run_id,
        "conf": conf or {}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in [200, 201]:
        raise RuntimeError(f"Failed to trigger DAG: {response.status_code}, {response.text}")

    print(f"Successfully triggered DAG run: {response.json()}")

def handler(event, context):
    data = event.get("data")
    if not data:
        print("[WARN] No data in Pub/Sub event")
        return

    try:
        decoded = base64.b64decode(data).decode()
        message = json.loads(decoded)
        print(f"[DEBUG] Decoded message: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to decode event: {e}")
        return

    file_name = message.get("name", "")
    print(f"[INFO] File uploaded: {file_name}")

    if not file_name.startswith("dags/") or "data_airflow.py" not in file_name:
        print(f"[INFO] Ignoring file: {file_name}")
        return

    # Build DAG Run ID
    run_id = f"dag-upload-{context.event_id}"

    # Optional: pass uploaded file name to DAG via conf
    conf = {"source_file": file_name}

    try:
        trigger_dag_run(DAG_ID, run_id, conf)
    except Exception as e:
        print(f"[ERROR] DAG trigger failed: {e}")
        raise

