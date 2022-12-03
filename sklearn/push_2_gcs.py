from google.cloud import storage

#https://stackoverflow.com/questions/37003862/how-to-upload-a-file-to-google-cloud-storage-on-python-3
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path_to_json_file'
storage_client = storage.Client()

bucket_name = "my-bucket"
