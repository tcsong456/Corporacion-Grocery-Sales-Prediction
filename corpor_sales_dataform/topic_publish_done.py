import argparse
from datetime import datetime
from google.cloud import pubsub_v1

def parse_args():
    arg = argparse.ArgumentParser()
    arg.add_argument('--project_id', type=str, required=True)
    arg.add_argument('--topic_id', type=str, required=True)
    return arg.parse_args()
args = parse_args()

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(args.project_id, args.topic_id)

data = b'dataform_completed'
attrs = {
    "tags": "prod",
    "date": datetime.utcnow().strftime("%Y-%m-%d"),
  }
publish = publisher.publish(topic_path, data, **attrs)
print('Published:', publish.result())