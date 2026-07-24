import os
from dotenv import load_dotenv
import boto3
import requests
from botocore.client import Config

load_dotenv()

endpoint = os.getenv("ENDPOINT_URL")
bucket = os.getenv("BUCKET_NAME")

client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

key = "cdms/umn/slac/idx/07180809_1920_F0010/07180809_1920_F0010.idx"

# Try HeadObject
try:
    r = client.head_object(Bucket=bucket, Key=key)
    print(f"HeadObject: SUCCESS")
    print(f"  ContentLength: {r.get('ContentLength')}")
    print(f"  ContentType: {r.get('ContentType')}")
    print(f"  ETag: {r.get('ETag')}")
except Exception as e:
    print(f"HeadObject: FAILED - {e}")

# Try GetObjectTagging
try:
    r = client.get_object_tagging(Bucket=bucket, Key=key)
    print(f"GetObjectTagging: SUCCESS - tags: {r.get('TagSet')}")
except Exception as e:
    print(f"GetObjectTagging: FAILED - {e}")

# Try GetObjectAttributes
try:
    r = client.get_object_attributes(Bucket=bucket, Key=key, ObjectAttributes=["ETag", "Checksum", "ObjectSize", "StorageClass"])
    print(f"GetObjectAttributes: SUCCESS")
    print(f"  {r}")
except Exception as e:
    print(f"GetObjectAttributes: FAILED - {e}")

# Try GetObject with specific request headers
url = client.generate_presigned_url(
    "get_object",
    Params={"Bucket": bucket, "Key": key},
)
# Try with range header
r = requests.get(url, headers={"Range": "bytes=0-1024"})
print(f"\nGET with Range: HTTP {r.status_code}")
print(f"  Body: {r.text[:200]}")
