import os
from minio import Minio
from minio.error import S3Error
from uuid import uuid4

# Connect to MinIO
minio_client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER", "admin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "password123"),
    secure=False
)

bucket_name = "stego-scans"

def init_minio():
    """Ensure the target bucket exists at startup."""
    try:
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
            print(f"Created MinIO bucket: {bucket_name}")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as err:
        print(f"MinIO Error: {err}")

def upload_file_to_minio(file_data: bytes, original_filename: str, file_extension: str) -> str:
    """
    Uploads file bytes to MinIO and returns the generated object name.
    """
    object_name = f"{uuid4()}{file_extension}"
    
    # Write bytes to a temporary local file to upload (MinIO python client prefers file paths or ByteIO streams)
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_data)
        temp_path = temp_file.name
        
    try:
        minio_client.fput_object(bucket_name, object_name, temp_path)
        return object_name
    except S3Error as err:
        print(f"Upload Error: {err}")
        return None
    finally:
        os.remove(temp_path)
