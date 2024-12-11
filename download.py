from botocore.client import Config
from boto3.session import Session
from dotenv import load_dotenv
import os
import concurrent


MIDFILES_DIR = "./raw/"


def get_aws_bucket():
    load_dotenv()
    config = Config(signature_version="s3v4")
    bucket = (
        Session(profile_name=os.getenv("PROFILE_NAME"))
        .resource(
            "s3",
            endpoint_url=os.getenv("ENDPOINT_URL"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            config=config,
            verify=True,
        )
        .Bucket("supercdms-data")
    )
    return bucket


def download_files():
    s3 = get_aws_bucket()
    for _, k in enumerate(s3.objects.limit(10).filter(Prefix="CDMS/UMN")):
        full_path = k.key
        if full_path.endswith(".mid.gz"):
            mid_file = full_path.split("/")[-1]
            mid_file_name = mid_file.split(".mid")[0]


def download_file(key: str):
    pass


download_files()
