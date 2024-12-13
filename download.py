from botocore.client import Config
from boto3.session import Session
from dotenv import load_dotenv
import os
import concurrent

MIDFILES_DIR = "./raw/"
BUCKET_PATH = "CDMS/UMN/R68/Raw/"


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
            # download file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(full_path, local_path)
            # extract channels
            proc = os.popen(f"./channel_extract {local_path}")
            proc.close()


def download_file(file: str):
    """
    Parameters
    ----------
    file(str): the mid file to download in the the format <filename>.mid.gz
    """
    s3 = get_aws_bucket()
    mid_file_name = file.split(".mid")[0]
    mid_prefix = "_".join(mid_file_name.split("_")[:2])

    s3.download_file(f"{BUCKET_PATH}{mid_prefix}/{file}", f"{MIDFILES_DIR}{file}")
    proc = os.popen(f"./channel_extract {MIDFILES_DIR}{file}")
    proc.close()
    print(f"finished download: {MIDFILES_DIR}{file}")


# download_files()
download_file("07180816_1648_F0006.mid.gz")
