import os
import re
import requests
import typer
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from rich.progress import Progress

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
    return filename != "" and (re.match(MID_PATTERN, filename) != None or re.match(FILE_PATTERN, filename) != None)


def download_routine(midfile: str, progress: Progress) -> tuple[str, Exception | None]:
    """
    UI Wrapper of download_dataset
    ----------------------------
    Parameters
    ----------
    midfile(str): the filename to download
    progress: The rich Progress object to keep track of downloads

    Returns
    -------
    Tuple(str, Exception|None): Returns an exception if input is invalid or operation failed, otherwise none.
    """
    if not isvalid_midfile(midfile):
        return (midfile, ValueError(f"[bold red]Must provide a valid mid file identifier,  i.e, 07180808_1558_F0001. File {midfile} is not valid[/bold red]"))

    try:
        download_dataset(midfile, progress)
        return (midfile, None)

    except Exception as e:
        return (midfile, e)


def download_dataset(midfile: str, progress: Progress):
    """
    Download dataset from storage (.idx, .csv, .txt)
    -----------------------------------------------------------------------------
    Parameters
    ----------
    file(str): the mid file to download in the the format 07180808_1558_F0001
    progress: The rich Progress object to keep track of downloads
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
        futures = [executor.submit(download_file, local_path, midfile, kv, progress) for kv in urls]

        for future in as_completed(futures):
            future.result()


def download_file(local_path: str, midfile: str, kv, progress: Progress):
    """
    Download a file from storage
    ----------------------------
    Parameters
    ----------
    local_path(str): the local path to write the file to
    midfile(str): the midfile to download
    kv: The key and url of the object
    progress: The rich Progress object to keep track of downloads
    """
    key, url = kv['key'], kv['url']
    file = os.path.basename(key)
    _, ext = os.path.splitext(file)

    b_resp = requests.get(url, stream=True)
    if b_resp.status_code != 200:
        typer.secho("could not retrieve object resource", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    total_size = int(b_resp.headers.get("Content-Length", 0))

    target_path = ""
    if ext == ".bin":
        bin_dir = os.path.join(local_path, midfile)
        os.makedirs(bin_dir, exist_ok=True)
        target_path = os.path.join(bin_dir, file)
    else:
        target_path = os.path.join(local_path, file)

    # keep track of progress for this file
    task_id = progress.add_task(
        "download",
        filename=f"{midfile}/{file}",
        total=total_size
    )

    with open(target_path, "wb") as f:
        for chunk in b_resp.iter_content(chunk_size=1024*1024):
            f.write(chunk)
            # update task progress
            progress.update(task_id, advance=len(chunk))

    # finished file download task
    progress.remove_task(task_id)
