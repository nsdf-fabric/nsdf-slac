from concurrent.futures import ThreadPoolExecutor, as_completed
import typer
from typing_extensions import Annotated
import os
import csv
from importlib import resources
from importlib.metadata import version as semver
from rich import print as richprint
from rich.console import Console
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TextColumn
from .download import download_routine


app = typer.Typer(no_args_is_help=True, help="NSDF Dark Matter CLI")
console = Console()
progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}"),
    BarColumn(),
    DownloadColumn(),
    TransferSpeedColumn(),
    TimeRemainingColumn(),
)


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
    filename: Annotated[ str, typer.Argument( help="The name of the file to download, i.e, 07180808_1558_F0001"), ] = "",
    filelist: Annotated[str, typer.Option("--file-list", "-f", help="A path to a text file listing the files to download")] = ""
):
    """
    Download a Dataset
    """
    files = set()
    errors = []
    # check if filelist flag is provided
    if filelist:
        if os.path.exists(filelist):
            with open(filelist, "r") as f:
                for line in f:
                    files.add(line.strip())
        else:
            errors.append(f"[bold red]path: {filelist} does not exists [/bold red]")
    else:
        files.add(filename.strip())

    if len(files) < 1:
        richprint("[bold red]Must provide at least 1 file[/bold red]")
        return

    with progress:
        with ThreadPoolExecutor(max_workers=min(len(files), 16)) as executor:
            futures = [executor.submit(download_routine, file, progress) for file in files]

            for future in as_completed(futures):
                midfile, result = future.result()
                if isinstance(result, Exception):
                    errors.append(f"[bold red] {result} [/bold red]")

    if len(errors) > 0:
        for err in errors:
            richprint(err)
    else:
        richprint(f"[bold green]Successfully downloaded {len(files)} dataset(s)![/bold green]")
