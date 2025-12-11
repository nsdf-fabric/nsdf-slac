import os
import re
import requests
import typer
from concurrent.futures import ThreadPoolExecutor
from rich import print as richprint

IDX_FILES_DIR = "./idx"
MID_PATTERN = r"^\d{8}_\d{4}_F\d{4}$"
FILE_PATTERN = r"^\d{8}_\d{4}_F\d{4}\.mid\.gz$"


def isvalid_midfile(filename: str) -> bool:
    """
    Check if the file provided is a valid mid identifier
    ----------------------------
    Parameters
    ----------
    filename(str): the filename to check
    """
    return filename != "" and (re.match(MID_PATTERN, filename) or re.match(FILE_PATTERN, filename))


def download_routine(midfile: str) -> (str, Exception | None):
    """
    UI Wrapper of download_dataset
    ----------------------------
    Parameters
    ----------
    midfile(str): the filename to download
    """
    if not isvalid_midfile(midfile):
        return (midfile, ValueError(f"[bold red]Must provide a valid mid file identifier,  i.e, 07180808_1558_F0001. File {midfile} is not valid[/bold red] "))

    try:
        richprint(f"[bold blue] Downloading {midfile}... [/bold blue]")
        download_dataset(midfile)
        return (midfile, None)

    except Exception as e:
        return (midfile, e)


def download_dataset(midfile: str):
    """
    Download dataset from storage (.idx, .csv, .txt)
    -----------------------------------------------------------------------------
    Parameters
    ----------
    file(str): the mid file to download in the the format 07180808_1558_F0001
    """
    local_path = os.path.join(IDX_FILES_DIR, midfile)
    if os.path.exists(local_path):
        return

    response = requests.get("https://services.nationalsciencedatafabric.org/api/v1/darkmatter/gen-url", params={"filename" : midfile})

    if response.status_code != 200:
        typer.secho("could not retrieve object resource", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    urls = response.json()['urls']
    os.makedirs(local_path, exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for kv in urls:
            executor.submit(download_file, local_path, midfile, kv)


def download_file(local_path, midfile, kv):
    """
    Download a file from storage
    ----------------------------
    Parameters
    ----------
    local_path(str): the local path to write the file to
    midfile(str): the midfile to download
    kv: The key and url of the object
    """
    key, url = kv['key'], kv['url']
    file = os.path.basename(key)
    _, ext = os.path.splitext(file)

    b_resp = requests.get(url, stream=True)
    if b_resp.status_code != 200:
        typer.secho("could not retrieve object resource", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    target_path = ""
    if ext == ".bin":
        bin_dir = os.path.join(local_path, midfile)
        os.makedirs(bin_dir, exist_ok=True)
        target_path = os.path.join(bin_dir, file)
    else:
        target_path = os.path.join(local_path, file)

    with open(target_path, "wb") as f:
        for chunk in b_resp.iter_content(chunk_size=8192):
            f.write(chunk)
