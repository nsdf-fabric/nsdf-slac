import re
import typer
from rich import print as richprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated
from concurrent.futures import ThreadPoolExecutor
import os
import requests
import csv
from importlib import resources
from importlib.metadata import version as semver

IDX_FILES_DIR = "./idx"
MID_PATTERN = r"^\d{8}_\d{4}_F\d{4}$"
FILE_PATTERN = r"^\d{8}_\d{4}_F\d{4}\.mid\.gz$"

app = typer.Typer(no_args_is_help=True, help="NSDF Dark Matter CLI")
console = Console()


def load_dataset():
    """
    Load Available Dataset
    """
    try:
        dataset = []
        with resources.files("nsdf_dark_matter_cli").joinpath("r_dataset.csv").open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dataset.append([row["filename"], row["size"], row["rseries"]])
    except Exception as e:
        richprint(f"[bold red]Failed to load dataset: {e}[/bold red]")
        raise typer.Exit(code=1)

    return dataset


DATASET = load_dataset()


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


def download_processed_files(midfile: str):
    """
    Download processed files from storage (idx, channel metadata, event metadata)
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


@app.command()
def version():
    """
    CLI Version
    """
    richprint(f"NSDF Dark Matter CLI: {semver('nsdf_dark_matter_cli')}")


@app.command()
def ls(prefix: Annotated[str, typer.Option("--prefix","-p",help="List all files that start with prefix")] = "",
       limit: Annotated[int, typer.Option("--limit","-l",help="The number of files to show")] = None):
    """
    List all available files
    """

    is_match = (lambda f: f.startswith(prefix)) if prefix else (lambda _: True)
    limit = (1_000_000 if prefix else 10) if (limit is None or limit < 0) else limit

    for entry in DATASET:
        if limit <= 0:
            break

        filename, size, rseries = entry
        if is_match(filename):
            richprint(f"[bold green]{filename}\t{size}\t{rseries}[/bold green]")
            limit -= 1

    richprint(f"[bold blue]Total Files Available: {len(DATASET)}[/bold blue]")


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
    Download a Dataset
    """
    if filename == "" or not(re.match(MID_PATTERN, filename) or re.match(FILE_PATTERN, filename)):
        richprint(
            f"[bold red]Must provide a valid mid file identifier, i.e, 07180808_1558_F0001[/bold red] "
        )
    else:
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
