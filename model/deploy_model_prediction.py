import os, json, uuid, time
import numpy as np
import pandas as pd
import lightgbm as lgb
from google.cloud import storage, bigquery, bigquery_storage, pubsub_v1
from google.cloud.bigquery import LoadJobConfig

project_id = os.environ['PROJECT_ID']
model_uri = os.environ['MODEL_URI']
src_table = os.environ['SRC_TABLE']
dst_table = os.environ['DST_TABLE']
region = os.environ['REGION']
chunk_rows = int(os.environ.get("chunk_rows", "25000"))
id_identifer = 'store_nbr,item_nbr'.split(',')

def pubsub_publish(project_id, topic_id, payload, attrs):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    data = json.dumps(payload).encode('utf-8')
    publish = publisher.publish(topic_path, data, **(attrs or {}))
    print('Published:', publish.result())

def load_model_from_gcs(gcs_uri):
    models, model_names = [], []
    temp_folder = 'tmp'
    os.makedirs(temp_folder, exist_ok=True)
    
    assert gcs_uri.startswith("gs://"), 'gcs uri must start with gs://'
    bucket_name, blob_name = gcs_uri.replace('gs://', '').split('/', 1)
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    
    for b in bucket.list_blobs(prefix=blob_name):
        _,model_name = b.name.split('/')
        local_path = os.path.join(temp_folder, model_name)
        b.download_to_filename(local_path)
        model = lgb.Booster(model_file=local_path)
        models.append(model)
        model_names.append(model_name)
    sorted_index = sorted(range(len(model_names)),key=lambda i:int(model_names[i].replace('.txt','').split('_')[-1]))
    models = [models[i] for i in sorted_index]
    return models

def page_query(client, sql, chunk_size, use_bq_client=False):
    job = client.query(sql)
    it = job.result(page_size=chunk_size)
    if use_bq_client:
        bqs = bigquery_storage.BigQueryReadClient()
        for df_page in it.to_dataframe_iterable(bqstorage_client=bqs):
            yield df_page
    else:
        for df_page in it.to_dataframe_iterable():
            yield df_page

def main():
    client = bigquery.Client(project=project_id)
    models = load_model_from_gcs(model_uri)
    
    col_expr = "*"
    query = f"SELECT {col_expr} FROM `{src_table}`"
    
    total_rows = 0
    write_mode = "WRITE_TRUNCATE"
    dates = pd.date_range(start='2017-8-16', end='2017-8-17').strftime("%Y-%m-%d").tolist()
    for df in page_query(client, query, chunk_rows):
        preds = []
        id_df = df[id_identifer].copy()
        features = [c for c in df.columns if c not in id_identifer]
        X = df[features].to_numpy(dtype=np.float32)
        for model in models:
            y = model.predict(X)
            y = np.asarray(y).reshape(-1,1)
            preds.append(y)
        predictions = np.concatenate(preds,axis=1)
        id_df[dates] = predictions
        chunk_preds = id_df.copy()
        
        job = client.load_table_from_dataframe(chunk_preds, dst_table,
                                               job_config=LoadJobConfig(write_disposition=write_mode),
                                               location=region)
        job.result()
        
        write_mode = "WRITE_APPEND"
        total_rows += len(chunk_preds)
        print(f"Wrote batch of {len(chunk_preds)} rows and (cumulative total of {total_rows} rows).", flush=True)
    
    dst_table_path = dst_table.split('.')
    preds_dataset = dst_table_path[1]
    preds_table = dst_table_path[2]
    pubsub_publish(
      project_id=project_id,
      topic_id='post-preds-topic',
      payload={
        "event": "predictions_loaded",
        "dataset": preds_dataset,
        "table": preds_table,
        "run_id": str(uuid.uuid4()),
        "ts": int(time.time()),
        },
    attrs={"source": "batch-loader", "stage": "final"}
  )

if __name__ == '__main__':
    main()