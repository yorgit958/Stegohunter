import io
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

def ensure_bucket(bucket_name: str):
    """Ensure the specified bucket exists, create it if not."""
    try:
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
    except S3Error as e:
        print(f"MinIO bucket check failed for {bucket_name}: {e}")

# Pre-create standard buckets on startup
try:
    ensure_bucket("originals")
    ensure_bucket("sanitized")
except Exception as e:
    print(f"Warning: Could not connect to MinIO on startup: {e}")

def upload_file_bytes(bucket_name: str, object_name: str, file_bytes: bytes, content_type: str = "application/octet-stream"):
    """Stream a raw byte array straight into MinIO."""
    ensure_bucket(bucket_name)
    data_stream = io.BytesIO(file_bytes)
    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data_stream,
            length=len(file_bytes),
            content_type=content_type
        )
        return True
    except S3Error as e:
        print(f"MinIO Upload Error: {e}")
        return False

def download_file_bytes(bucket_name: str, object_name: str) -> bytes:
    """Download an object from MinIO and return its raw bytes."""
    try:
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    except S3Error as e:
        print(f"MinIO Download Error: {e}")
        return None
