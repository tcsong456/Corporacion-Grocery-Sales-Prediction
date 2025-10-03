import os, json, base64
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request, Response
from google.cloud import bigquery, storage

project = os.environ['project_id']
dataset = os.environ['bq_dataset']
table = os.environ['bq_table']
region = os.environ['region']
data_bucket = os.environ['data_bucket']

app = FastAPI()

def create_submission(client, store_item, test):
    print('reading dataset form bigquery and create submission')
    query = """
      SELECT * FROM
      `corpor_sales_submission.corpor_preds`
    """
    df = client.query(query).to_dataframe()
    
    df = df.merge(store_item,how='left',on=['store_nbr','item_nbr']).fillna(0)
    dates = list(map(str, pd.date_range('2017-08-16','2017-08-17',freq='D').date))
    def apply_filter(row):
        if row['indicator'] == 0:
            row[dates] = 0
        return row
    df = df.apply(apply_filter,axis=1)
    df = df.melt(id_vars=['store_nbr','item_nbr'],
                  value_vars=dates,
                  var_name='date',
                  value_name='sales')
    df['sales'] = np.expm1(df['sales'])
    df['store_nbr'] = df['store_nbr'].astype(np.int8)
    df['item_nbr'] = df['item_nbr'].astype(np.int32)
    df['sales'] = df['sales'].astype(np.float32)
    
    df = df.merge(test[['store_nbr','item_nbr','id','date']],how='left',on=['store_nbr','item_nbr','date'])
    df['sales'] = df['sales'].clip(lower=0,upper=1000)
    submission = df[['id','sales']]
    return submission

def upload_submission(client, sub_file):
    bucket = client.bucket(data_bucket)
    blob = bucket.blob('corpor_submission.csv')
    blob.upload_from_filename(sub_file)
    print('successfully uploaded the submission.csv file')
    return Response(status_code=204)

@app.post("/")
async def receive(request: Request):
    body = await request.json()
    msg = body.get("message", {})
    data_b64 = msg.get("data")
    if 'message' not in body:
        print('status: bad request')
        return
    
    if not data_b64:
        print('status: no data')
        return
    
    payload = json.loads(base64.b64decode(data_b64).decode("utf-8"))
    attrs = msg.get("attributes", {})
    if payload.get("event") != "predictions_loaded":
        return Response(status_code=400)

    run_id = payload.get("run_id")
    dataset_id, table_id = payload.get('dataset'), payload.get('table')
    print(f'payload attributes: {attrs} and run id: {run_id}')
    
    if dataset_id != dataset or table_id != table:
        print('failed due to different table targeted')
        return Response(status_code=400)
    
    os.makedirs('tmp', exist_ok=True)
    
    unique_pairs = set()
    for chunk in pd.read_csv(f'gs://{data_bucket}/train.csv',
                             chunksize=200_000,
                             usecols=['store_nbr','item_nbr'],
                             dtype={'store_nbr':'int16','item_nbr':'int32'},
                             storage_options={"token":"cloud"}):
        unique_pairs.update(zip(chunk['store_nbr'].to_numpy(), chunk['item_nbr'].to_numpy()))
    
    store_item = pd.DataFrame(list(unique_pairs), columns=['store_nbr','item_nbr'])
    store_item['indicator'] = 1
    
    test = pd.read_csv(f'gs://{data_bucket}/test.csv')
    sub_file = 'tmp/submission.csv'

    bq_client = bigquery.Client(project=project)
    storage_client = storage.Client(project=project)
    
    submission = create_submission(bq_client, store_item, test)
    submission.to_csv(sub_file, index=False)
    upload_submission(storage_client, sub_file)

@app.get("/health")
def health():
    return {"ok": True}
    

#%%

