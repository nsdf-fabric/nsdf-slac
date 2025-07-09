# NSDF Dark Matter Library

The `nsdf_dark_matter` library offers a pool of operations to work with the `R68` dark matter dataset.
Once you've downloaded the dataset using the NSDF Dark Matter CLI, this library helps you load and explore the data with a Python API.

## Prerequisites

If you do not have already an `idx` directory with dark matter datasets, you can check the [CLI guide](./cli.md) for a step by step walkthrough
on how to obtain a dataset.

## Getting Started

### Importing the Library

First, lets import the `load_all_data` function from the idx module.

```python
from nsdf_dark_matter.idx import load_all_data
```

### Loading a dataset

To work with the different operations of the library, we need to start by loading the dataset as follows.

```python
# specify the path to the dataset you want to use
cdms = load_all_data('idx/07180827_0000_F0001')
```

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

### Getting Detector IDs

Similarly, we can query for all the detector IDs of the dataset.

```python
detector_ids = cdms.get_detector_ids()
```

### Retrieving Channel Data

Let's get the channel data for our first detector with the `get_detector_channels` method.

```python
channel_data =  cdms.get_detector_channels(detector_ids[0])
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

### Full Example

```python
from nsdf_dark_matter.idx import load_all_data

# Loading the data from a valid idx structure
cdms = load_all_data('idx/07180827_0000_F0001')

# getting all event ids
event_ids = cdms.get_event_ids()

# getting the metadata for the first event
metadata = cdms.get_event_metadata(event_ids[0])

# getting all detector ids
detector_ids = cdms.get_detector_ids()

# getting channels associated with a the first detector id
channel_data =  cdms.get_detector_channels(detector_ids[0])

# getting all detectors for the last event id
dec_ids = cdms.get_detectors_by_event(event_ids[-1])
# channel data for those detectors
for detector_id in dec_ids:
    channel_data = cdms.get_detector_channels(detector_id)
```

## What's Next?

Now that you can manipulate the data, you could:

- 🔄 Integrate into larger workflows.
- 🤖 Build machine learning pipelines for dark matter.
- 📊 Build dark matter dashboards

We have provided a web-based visualization of the entire dataset with the [NSDF Dark Matter Dashboard](https://services.nationalsciencedatafabric.org/darkmatter). Check the [dashboard guide](./dashboard.md) to learn more about its components!
