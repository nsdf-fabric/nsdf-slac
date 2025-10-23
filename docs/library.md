# NSDF Dark Matter Library

The `nsdf_dark_matter` library offers a pool of operations to work with dark matter datasets (R68, R76).
Once you've downloaded the dataset using the NSDF Dark Matter CLI, this library helps you load and explore the data with a Python API.

## Prerequisites

!!! note "Prerequisites"

    If you do not have already an `idx` directory with dark matter datasets, you can check the [CLI guide](./cli.md) for a step by step walkthrough
    on how to obtain a dataset. If you are following from the CLI guide you can use the same environment and skip to [Installing the Library](#installing-the-library)

## 🚀 Getting Started

!!! info "Virtual Environment"

    To begin, make sure you have Python 3.10 or higher installed on your machine. You can download it from the official website: [Install Python](https://www.python.org/downloads/).

    In this guide, we will be using [uv](https://docs.astral.sh/uv/) to manage a virtual environment. You can install `uv` by following this [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

!!! note

    If you prefer, you can use a different environment manager such as [conda](https://www.anaconda.com/docs/getting-started/miniconda/main) or Python's built-in [venv](https://docs.python.org/3/library/venv.html).

### Creating the environment

To create a new virtual environment, run the following command in your terminal:

=== "uv (recommended)"

    !!! info "uv (recommended)"

        ```bash
        uv venv darkmatter_lib_env --python 3.10
        ```

=== "Conda"

    !!! info "Conda"

        ```bash
        conda create -n darkmatter_lib_env python=3.10
        ```

=== "Python venv"

    !!! info "Python venv"

        ```bash
        python -m venv darkmatter_lib_env
        ```

### Activating the environment

Next, we activate the environment:

=== "uv (recommended)"

    !!! info "uv (recommended)"

        ```bash
        source darkmatter_lib_env/bin/activate
        ```

=== "Conda"

    !!! info "Conda"

        ```bash
        conda activate darkmatter_lib_env
        ```

=== "Python venv"

    !!! info "Python venv"

        ```bash
        source darkmatter_lib_env/bin/activate
        ```

---

You should now see the environment name in your terminal prompt, indicating it’s active.

### Installing the Library

#### pip (recommended)

To install the library via pip, run the following command:

!!! info "Library pip installation"

    ```bash
    pip install nsdf-dark-matter
    ```

#### From Release

To install the library from releases, download the `wheel` file.

```bash
wget https://github.com/nsdf-fabric/nsdf-slac/releases/download/v0.1.0/nsdf_dark_matter-0.1.0-py3-none-any.whl
```

=== "uv (recommended)"

    !!! info "uv (recommended)"

        ```bash
        uv pip install nsdf_dark_matter-0.1.0-py3-none-any.whl
        ```

=== "Conda"

    !!! info "Conda"
        ```bash
        pip install nsdf_dark_matter-0.1.0-py3-none-any.whl
        ```

=== "Python venv"

    !!! info "Python venv"

        ```bash
        pip install nsdf_dark_matter-0.1.0-py3-none-any.whl
        ```

---

That's it! The library is now installed and ready to use. We can start working with it.

## 📚 NSDF Dark Matter Library

### Importing the Library

First, import the `load_all_data` function from the idx module.

```python
from nsdf_dark_matter.idx import load_all_data
```

### Loading a dataset

To work with the different operations of the library, we need to start by loading the dataset as follows.

```python
# specify the path to the dataset you want to use
cdms = load_all_data('idx/07180827_0000_F0001')
```

## ⚡Event Methods

### Getting event IDs

We can query for all the event IDs of the dataset like so.

```python
event_ids = cdms.get_event_ids()
```

### Obtaining Event Metadata

Let's fetch the event metadata of our first event with the `get_event_metadata` method.

```python
metadata = cdms.get_event_metadata(event_ids[0])
```

### Getting All Detectors of an Event

We can query to all the detectors of an event with the `get_detectors_by_event` method.
Let's do that for our last event.

```python
dec_ids = cdms.get_detectors_by_event(event_ids[-1])

# channel data for those detectors
for detector_id in dec_ids:
    channel_data = cdms.get_detector_channels(detector_id)
```

## ⚙️Detector methods

### Getting Detector IDs

Similarly, we can query for all the detector IDs of the dataset.

```python
detector_ids = cdms.get_detector_ids()
```

### Retrieving Channel Data

Let's get the channel data for our first detector with the `get_detector_channels` method.

```python
channel_data = cdms.get_detector_channels(detector_ids[0])
```

## Full Example

=== "main.py"

    ``` python
    from nsdf_dark_matter.idx import load_all_data

    # Loading the data from a valid idx structure
    cdms = load_all_data('idx/07180827_0000_F0001')

    # getting all event ids
    event_ids = cdms.get_event_ids()

    # getting the metadata for the first event
    metadata = cdms.get_event_metadata(event_ids[0])

    # getting all detectors for the last event id
    dec_ids = cdms.get_detectors_by_event(event_ids[-1])

    # channel data for those detectors
    for detector_id in dec_ids:
        channel_data = cdms.get_detector_channels(detector_id)

    # getting all detector ids
    detector_ids = cdms.get_detector_ids()

    # getting channels associated with a the first detector id
    channel_data = cdms.get_detector_channels(detector_ids[0])
    ```

## Next Steps

Now that you can manipulate the data, you could:

- 🔄 Integrate into larger workflows.
- 🤖 Build machine learning pipelines for dark matter.
- 📊 Build dark matter dashboards

We have provided a web-based visualization of the entire dataset with the [NSDF Dark Matter Dashboard](https://services.nationalsciencedatafabric.org/darkmatter). Check the [dashboard guide](./dashboard.md) to learn more about its components!
