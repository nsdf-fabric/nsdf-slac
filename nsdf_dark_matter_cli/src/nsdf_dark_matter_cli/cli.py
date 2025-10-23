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

IDX_FILES_DIR = "./idx"
MID_PATTERN = r"^\d{8}_\d{4}_F\d{4}$"
FILE_PATTERN = r"^\d{8}_\d{4}_F\d{4}\.mid\.gz$"

__version__ = "0.3.0"


def load_dataset() -> list[str, str, str]:
    dataset = []
    with resources.files("nsdf_dark_matter_cli").joinpath("r_dataset.csv").open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset.append([row["filename"], row["size"], row["rseries"]])

    return dataset


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


app = typer.Typer(no_args_is_help=True, help="NSDF Dark Matter CLI")
console = Console()


@app.callback()
def main(
    ctx: typer.Context,
):
    try:
        ctx.obj = load_dataset()
    except Exception as e:
        richprint(f"[bold red]Failed to load dataset: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def version():
    """
    Shows the semantic versioning of the CLI
    """
    richprint(f"NSDF Dark Matter CLI: {__version__}")


@app.command()
def ls(ctx: typer.Context,
       prefix: Annotated[str, typer.Option("--prefix","-p",help="List all files that start with prefix")] = "",
       limit: Annotated[int, typer.Option("--limit","-l",help="The number of files to show")] = 100):
    """
    List all the files available to download from remote
    """
    dataset = ctx.obj

    if limit < 0 or limit > len(dataset):
        richprint(f"[bold red] Invalid limit set {limit}[/bold red]")
        return

    # prefix option
    if prefix:
        for entry in dataset:
            filename, size, rseries = entry[0], entry[1], entry[2]
            if filename.startswith(prefix) and limit:
                richprint(f"[bold green]{filename}\t{size}\t{rseries}[/bold green]")
                limit -= 1
        return

    # limit option
    for i in range(0, limit):
        richprint(f"[bold green]{dataset[i][0]}\t{dataset[i][1]}\t{dataset[i][2]}[/bold green]")


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
