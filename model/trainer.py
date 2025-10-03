import argparse, json, os
import numpy as np
import pandas as pd
import lightgbm as lgb
from google.cloud import bigquery, storage

MAX_ROUNDS = 500
PREDICT_DAYS = 2

def parse_args():
    arg = argparse.ArgumentParser()
    
    arg.add_argument('--learning_rate', type=float, default=0.1)
    arg.add_argument('--num_leaves', type=int, default=31)
    arg.add_argument('--max_depth', type=int, default=-1)
    arg.add_argument('--feature_fraction', type=float, default=0.8)
    arg.add_argument('--bagging_fraction', type=float, default=0.8)
    arg.add_argument('--bagging_freq', type=int, default=1)
    arg.add_argument('--lambda_l1', type=float, default=0.0)
    arg.add_argument('--lambda_l2', type=float, default=0.0)
    arg.add_argument('--min_data_in_leaf', type=int, default=100)
    arg.add_argument('--early_stopping_rounds', type=int, default=100)
    
    arg.add_argument('--best_params_json', default='')
    arg.add_argument('--mode', default='hpt')
    return arg.parse_args()

def load_df_from_bq(bq, project, dataset, table):
    table_ref = f"`{project}.{dataset}.{table}`"
    sql = f"SELECT * FROM {table_ref}"
    df = bq.query(sql).result().to_dataframe(create_bqstorage_client=True)
    df = df.fillna(0)
    return df
  
def gcs_upload(local_path, gcs_uri, project):
    assert gcs_uri.startswith("gs://")
    bucket_name, blob_name = gcs_uri[5:].split("/", 1)
    if not bucket_name or not blob_name:
      raise ValueError('URI must contain both bucket_name and blob_name')
    
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"local file not found: {local_path}")
    
    client = storage.Client(project=project)
    bucket = client.lookup_bucket(bucket_name)
    if bucket is None:
        bucket = client.create_bucket(bucket_name, location="europe-west1")
    blob = bucket.blob(blob_name)
    
    blob.upload_from_filename(local_path)

def report_metric(metric, value):
    try:
        from hypertune import HyperTune
        HyperTune().report_hyperparameter_tuning_metric(
          hyperparameter_metric_tag=metric,
          metric_value=float(value),
          global_step=0)
    except Exception as e:
        print(f"hypertune report failed: {e}")


def fit_eval(params, Xtr, ytr, Xval, yval, items, args):
    val_preds,models = [],[]
    Xtr = Xtr.merge(items[['item_nbr', 'perishable']],how='left',on=['item_nbr'])
    columns = Xtr.columns
    valid_cols = [c for c in columns if c not in  ['item_nbr', 'store_nbr', 'perishable']]
    weight_tr = Xtr['perishable'] * 0.25 + 1
    Xval = Xval.merge(items[['item_nbr', 'perishable']],how='left',on=['item_nbr'])
    weight_val = Xval['perishable'] * 0.25 + 1
    d_train = np.array(Xtr[valid_cols])
    d_val = np.array(Xval[valid_cols])
    label_cols = [c for c in ytr.columns if c not in ['store_nbr', 'item_nbr']]
    y_tr = np.array(ytr[label_cols])
    y_val = np.array(yval[label_cols])
    
    for i in range(PREDICT_DAYS):
        dtrain = lgb.Dataset(
          d_train, label=y_tr[:, i],
          weight=np.array(weight_tr)
          )
        
        dval = lgb.Dataset(
          d_val, label=y_val[:, i], reference=dtrain,
          weight=np.array(weight_val)
          )
        
        model = lgb.train(
          params, dtrain, num_boost_round=MAX_ROUNDS,
          valid_sets=[dtrain, dval]
          )
        val_preds.append(model.predict(
          d_val, num_iteration=model.best_iteration or MAX_ROUNDS)
          )
        models.append(model)
    
    preds = np.array(val_preds).transpose()
    err = (y_val[:, :PREDICT_DAYS] - preds)**2
    err = err.sum(axis=1) * weight_val
    err = np.sqrt(err.sum() / weight_val.sum() / PREDICT_DAYS)
    print(f'overall rmse loss is: {err:.4f}')
    return models, err

def main():
    bq_project = os.environ.get('bq_project')
    bq_dataset = os.environ.get('bq_dataset')
    train_table = os.environ.get('train_table')
    valid_table = os.environ.get('valid_table')
    label_train = os.environ.get('label_train')
    label_val = os.environ.get('label_val')
    items_table = os.environ.get('items_table')
    metric = os.environ.get('metric')
    prefix_model_dir = os.environ.get('AIP_MODEL_DIR')
    required_dict = {
        "bq_project": bq_project,
        "bq_dataset": bq_dataset,
        "train_table": train_table,
        "valid_table": valid_table,
        "label_train": label_train,
        "label_val": label_val,
        "items_table": items_table,
        "metric": metric,
        "prefix_model_dir": prefix_model_dir
      }
    missing_reqs = []
    for key, value in required_dict.items():
        if not value:
          missing_reqs.append(key)
    if missing_reqs:
      raise RuntimeError(f"missing required parameterL: {', '.join(missing_reqs)}")

    path = prefix_model_dir.replace("gs://","")
    parts = path.split('/')
    parts = parts[1:]
    if len(parts) >= 2:
      trial_id = parts[-2]
    else:
      trial_id = None
    
    args = parse_args()
    if args.best_params_json.strip():
        try:
            best_params = json.load(args.best_params_json)
            for k,v in best_params.items():
              if hasattr(args, k):
                setattr(args, k, v)
        except Exception as e:
          print(f'bad param json: {e}')
    
    params = {
        'objective': "regression",
        'learning_rate': args.learning_rate,
        'num_leaves': args.num_leaves,
        'max_depth': args.max_depth,
        'min_data_in_leaf': args.min_data_in_leaf,  
        'feature_fraction': args.feature_fraction,
        'bagging_fraction': args.bagging_fraction,
        'bagging_freq': args.bagging_freq,
        'lambda_l1': args.lambda_l1,
        'lambda_l2': args.lambda_l2,
        'early_stopping_rounds': args.early_stopping_rounds,
        'metric': 'l2'
      }
    print("hyperparameters:", json.dumps(params, indent=2))
      
    bq = bigquery.Client(project=bq_project)
    dates = ['2017614','2017621','2017628','2017705','2017712','2017719']
    x_tr, y_tr = [], []
    for date in dates:
      train_table_nm = f'{train_table}_{date}'
      label_train_nm = f'{label_train}_{date}'
      xtr = load_df_from_bq(bq, bq_project, bq_dataset, train_table_nm)
      ytr = load_df_from_bq(bq, bq_project, bq_dataset, label_train_nm)
      ytr = xtr[['store_nbr', 'item_nbr']].merge(ytr, how='left', on=['store_nbr', 'item_nbr'])
      x_tr.append(xtr)
      y_tr.append(ytr)
    x_tr = pd.concat(x_tr)
    y_tr = pd.concat(y_tr)
      
    x_val = load_df_from_bq(bq, bq_project, bq_dataset, valid_table)
    y_val = load_df_from_bq(bq, bq_project, bq_dataset, label_val)
    y_val = x_val[['store_nbr', 'item_nbr']].merge(y_val, how='left', on=['store_nbr', 'item_nbr'])
    items = load_df_from_bq(bq, bq_project, bq_dataset, items_table)
  
    models, rmse = fit_eval(params, x_tr, y_tr, x_val, y_val, items, args)
    if args.mode == 'hpt':
        report_metric(metric, rmse)
        os.makedirs('/tmp/model', exist_ok=True)
        for i,model in enumerate(models):
            model_name = f'model_lgb_{i}.txt'
            model.save_model(f"/tmp/model/{model_name}")
            model_dir = os.path.join(prefix_model_dir, model_name)
            gcs_upload(f"/tmp/model/{model_name}", model_dir, bq_project)
        
        with open('/tmp/model/metadata.json', 'w') as f:
            json.dump({'mode': 'hpt', 'trial_id': trial_id, "rmse": rmse}, f, indent=2)
        metadata_dir = os.path.join(prefix_model_dir, 'metadata.json')
        gcs_upload("/tmp/model/metadata.json", metadata_dir, bq_project)
    else:
        os.makedirs('/tmp/final', exist_ok=True)
        bucket = prefix_model_dir.replace("gs://","").split('/')[0]
        final_model_dir = os.path.join("gs://", bucket)
        for i in range(PREDICT_DAYS):
            model = models[i]
            model_name = f'final_lgb_model_{i}.txt'
            model.save_model(f'/tmp/final/{model_name}')
            model_dir = os.path.join(final_model_dir, 'final', model_name)
            gcs_upload(f'/tmp/final/{model_name}', model_dir, bq_project)
        
if __name__ == '__main__':
    main()


