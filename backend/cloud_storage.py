# cloud_storage.py
from google.cloud import storage
import os

# Assumes that your GOOGLE_APPLICATION_CREDENTIALS is set
def upload_file_to_bucket(source_file, bucket_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file)
    return f"gs://{bucket_name}/{destination_blob_name}"
