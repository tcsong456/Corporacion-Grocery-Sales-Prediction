import os
import numpy as np
import lightgbm as lgb
from fastapi import FastAPI, HTTPException, Body
from google.cloud import storage

app = FastAPI()
MODELS = []

def download_model_from_gcs(gcs_model_uri, local_model_path):
    assert gcs_model_uri.startswith('gs://'), f'gcs_model_uri must be a gcs uri,but got: {gcs_model_uri}'
    bucket_name, prefix = gcs_model_uri[5:].split('/', 1)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    os.makedirs(local_model_path, exist_ok=True)
    
    i = 0
    model_paths = []
    for blob in bucket.list_blobs(prefix=prefix.rstrip('/') + '/'):
        if blob.name.endswith('.txt'):
            local_path = os.path.join(local_model_path, f'lgb_model_{i}.txt')
            blob.download_to_filename(local_path)
            model_paths.append(local_path)
            i += 1
    
    if not model_paths:
        raise FileNotFoundError(f"No .txt or .lgb files found under {gcs_model_uri}")
      
    return model_paths

@app.on_event('startup')
def _load():
  global MODELS
  
  gcs_uri = os.environ.get('AIP_STORAGE_URI')
  if not gcs_uri:
      raise RuntimeError("base_output_directory env var is not set in the custome job in trainer script")
  model_paths = download_model_from_gcs(gcs_uri, '/tmp/lgb_models/')
  for model_path in model_paths:
      model = lgb.Booster(model_file=model_path)
      MODELS.append(model)
  if not MODELS:
      raise RuntimeError("No models loaded.")

def to_2d_array(instances):
    if not isinstance(instances, list):
        raise ValueError("instances must be a list")
    if len(instances) == 0:
        return np.empty((0, 0), dtype=float)

    first = instances[0]
    if isinstance(first, dict):
        keys = list(first.keys())
        arr = np.array([[float(row.get(k, 0.0)) for k in keys if k not in ['store_nbr', 'item_nbr']] for row in instances], dtype=float)
    else:
        arr = np.array(instances, dtype=float)
        arr = arr[:,2:]

    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if arr.ndim != 2:
        raise ValueError("instances must be convertible to a 2D array")
    return arr

@app.post('/predict')
def predict(payload: dict = Body(...)):
  preds = []
  try:
      instances = payload.get('instances')
      if instances is None:
          print('no instances available')
          raise HTTPException(status_code=400, detail="Payload must contain 'instances'")
      X = to_2d_array(instances)
      for MODEL in MODELS:
          pred = MODEL.predict(X)
          preds.append(pred)
      preds = np.array(preds).transpose()
      return {'predictions': preds.tolist()}
  except Exception as e:
      print(f'inside the app prediction serving image,error: {e}')
      raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health():
    return {'status': 'ok'}
    
#%%

