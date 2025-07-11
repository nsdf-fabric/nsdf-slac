# NSDF Dark Matter CLI

The `nsdf_dark_matter` CLI offers a pool of operations to access and download the R68 dark matter dataset. The CLI serves as a top level component in a workflow to download data which can
then be analyzed with the [NSDF Dark Matter Library](https://github.com/nsdf-fabric/nsdf-slac/tree/main/nsdf_dark_matter)

## Getting Started

### 🐍 Python tooling

Before getting started, make sure you have Python 3.10 or higher installed on your machine. You can download it from the official website: [Install Python](https://www.python.org/downloads/).

In this guide, we will be using [uv](https://docs.astral.sh/uv/) to manage a virtual environment. You can install `uv` by following this [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

> **_NOTE:_** If you prefer, you can use a different environment manager such as [conda](https://www.anaconda.com/docs/getting-started/miniconda/main) or Python's built-in [venv](https://docs.python.org/3/library/venv.html).

### 🧪 Creating the environment

To create a new virtual environment using uv, run the following command in your terminal:

```bash
uv venv darkmatter_env --python 3.10
```

This creates an isolated Python environment named darkmatter_env.

### ⚡Activating the environment

Next, activate the environment with:

```bash
source darkmatter_env/bin/activate
```

You should now see the environment name in your terminal prompt, indicating it’s active.

### 🚀 Installing the CLI

We are ready to install the CLI. First, download the `wheel` file.

```bash
wget https://github.com/nsdf-fabric/nsdf-slac/releases/download/v0.1.0/nsdf_dark_matter_cli-0.1.0-py3-none-any.whl
```

Now, we can install the CLI by passing the wheel file with the following uv command:

```bash
uv pip install nsdf_dark_matter_cli-0.1.0-py3-none-any.whl
```

That's it! The CLI is now installed and ready to use. We can start working with it.

### The NSDF Dark Matter CLI

To explore all available CLI commands and options, run the following help command:

```bash
nsdf-cli --help
```

![Help Command](../assets/cli/cli-help.gif)

### Listing remote files

Want to know what files are available to download? Use the ls command to list them. You can also limit how many results you see by passing the `--limit` flag.

```bash
nsdf-cli ls --limit 5
```

![List command](../assets/cli/cli-ls.gif)

Looking for something specific? Use the `--prefix` flag to filter files by name:

```bash
nsdf-cli ls --prefix 07180928_2310
```

### Downloading a dataset locally

Once you've found the file you want, downloading it is easy with the `download` command:

```bash
nsdf-cli download 07180827_0000_F0001
```

![Download Command](../assets/cli/cli-download.gif)

Downloaded files go into the idx directory, and each one gets its own subfolder based on the mid_id. After downloading a few datasets, your folder might look like this:

```console
idx/
   |
   07180925_0000_F0001/
   |
   07181007_0000_F0001/
   |
   07180916_0000_F0002/
```

## What's Next?

Now that you have some data, it’s time to dive into analysis! Head over to the [NSDF Dark Matter Library guide](./library.md) to learn how to start working with the dataset.
