import re
import typer
from rich import print as richprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.client import Config
from boto3.session import Session
import os

PREFIX = "CDMS/UMN/SLAC/idx/"
IDX_FILES_DIR = "./idx"
MID_PATTERN = r"^\d{8}_\d{4}_F\d{4}$"
FILE_PATTERN = r"^\d{8}_\d{4}_F\d{4}\.mid\.gz$"

__version__ = "0.0.1"

aws_config = """
"""

aws_creds = """
"""


def get_aws_bucket(verify=True):
    """
    Load AWS bucket given config
    """
    load_dotenv()

    config = Config(signature_version="s3v4")
    endpoint_url = os.getenv("ENDPOINT_URL")
    bucket_name = os.getenv("BUCKET_NAME")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    bucket = (
        Session()
        .resource(
            "s3",
            endpoint_url=endpoint_url,
            config=config,
            verify=verify,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        .Bucket(bucket_name)
    )
    return bucket


def check_if_key_exists(key: str, verify: bool) -> bool:
    """
    Check if a given key exists in the bucket
    ----
    Return
    bool: True if the key is in the bucket, False otherwise
    """
    if key == "":
        return False

    s3 = get_aws_bucket(verify)
    try:
        obj = s3.Object(key)
        obj.load()
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        # other error
        return False


def download_processed_files(midfile: str):
    """
    Download processed files from storage (idx, channel metadata, event metadata)
    -----------------------------------------------------------------------------
    Parameters
    ----------
    file(str): the mid file to download in the the format 07180808_1558_F0001
    """
    s3 = get_aws_bucket()

    filenames = [f"{midfile}.idx", f"0000.bin", f"{midfile}.txt", f"{midfile}.csv"]
    download_files = [
        os.path.join(PREFIX, midfile, filenames[0]),
        os.path.join(PREFIX, midfile, filenames[1]),
        os.path.join(PREFIX, midfile, filenames[2]),
        os.path.join(PREFIX, midfile, filenames[3]),
    ]

    for i, file in enumerate(download_files):
        dst = os.path.join(IDX_FILES_DIR, midfile, filenames[i])
        if filenames[i].split(".")[1] == "bin":
            dst = os.path.join(IDX_FILES_DIR, midfile, midfile, filenames[i])

        if not os.path.exists(dst):
            if check_if_key_exists(file, True):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                s3.download_file(file, dst)
            else:
                raise FileNotFoundError(f"{midfile} does not exists in storage")


app = typer.Typer(no_args_is_help=True, help="NSDF SLAC CLI")
configpath, credpath = ".aws/config", ".aws/credentials"
console = Console()


@app.command()
def version():
    """
    Shows the semantic versioning of the CLI
    """
    richprint(f"NSDF SLAC CLI: {__version__}")


@app.command()
def config():
    """
    Run this command to configure credentials to use the CLI
    """
    homedir = os.path.expanduser("~")
    config_path = os.path.join(homedir, configpath)
    cred_path = os.path.join(homedir, credpath)

    if not os.path.exists(config_path):
        os.makedirs(config_path, exist_ok=True)

    if not os.path.exists(cred_path):
        os.makedirs(cred_path, exist_ok=True)

    with open(config_path, "r") as f:
        if aws_config not in f.read():
            with open(config_path, "a") as fw:
                fw.write(aws_config)
                richprint("[bold green]Configuration created![/bold green]")
        else:
            richprint("[bold green]Configuration active[/bold green]")

    with open(cred_path, "r") as f:
        if aws_creds not in f.read():
            with open(cred_path, "a") as fw:
                fw.write(aws_creds)
                richprint("[bold green]Credentials created![/bold green]")
        else:
            richprint("[bold green]Credentials active[/bold green]")


@app.command()
def download(
    filename: Annotated[
        str,
        typer.Argument(
            help="The name of the file to download, i.e, 07180808_1558_F0001"
        ),
    ] = "",
):
    """
    Download all processed files derived from mid file (idx, channel metadata, event metadata)
    """
    if filename == "":
        richprint(
            f"[bold red]Must provide a valid mid file identifier, i.e, 07180808_1558_F0001[/bold red] "
        )
    else:
        if re.match(MID_PATTERN, filename) or re.match(FILE_PATTERN, filename):
            try:

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(
                        description="Downloading files...",
                        total=None,
                    )
                    download_processed_files(filename)
                richprint(
                    f"[bold green]{filename} processed files have been downloaded![/bold green]"
                )
            except Exception as e:
                richprint(
                    f"[bold red]Error fetching the processed files for {filename} {e}[/bold red]"
                )
        else:
            richprint(
                f"[bold red]Must provide a valid mid file identifier, i.e, 07180808_1558_F0001[/bold red] "
            )


if __name__ == "__main__":
    app()
