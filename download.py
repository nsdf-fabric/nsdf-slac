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
            local_path = f"{MIDFILES_DIR}{mid_file}"
            # donwload file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(full_path, local_path)
            # extract channels
            os.popen(f"./channel_extract {local_path}")


download_files()
