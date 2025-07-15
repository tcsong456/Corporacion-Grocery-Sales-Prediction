import os
import sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from tqdm import tqdm
from google.cloud import storage
from google.oauth2 import service_account

class FileUploadeWrapper:
    def __init__(self,
                 file_obj,
                 file_name,
                 total_size,
                 chunk_size):
        self.file_obj = file_obj
        self.progress_bar = tqdm(total=total_size, unit_scale=True, unit='B', desc=f'Uploading file:{file_name}')
        self.chunk_size = chunk_size
    
    def read(self,size=None):
        data = self.file_obj.read(size or self.chunk_size)
        self.progress_bar.update(len(data))
        return data
    
    def __getattr__(self, attr):
        return getattr(self.file_obj, attr)

def upload_if_not_exists(bucket_name,blob_name,local_path,verbose=None):
    creds = service_account.Credentials.from_service_account_file('key.json')
    client = storage.Client(credentials=creds)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    file = os.path.basename(local_path)
    name_index = file.find('.')
    file_name = file[:name_index]
    if not blob.exists():
        assert verbose is not None,'when blob not exist,verbose need to be specified'
        if verbose:
            total_size = os.path.getsize(local_path)
            with open(local_path,'rb') as f:
                file_uploader = FileUploadeWrapper(f, file_name, total_size, 1024*1024*256)
                blob.upload_from_file(file_uploader)
        else:
            blob.upload_from_filename(local_path)
    else:
        print(f'file:{file_name} already uploaded')
    return blob
            
        