# NSDF Dark Matter Library

The `nsdf_dark_matter` library offers a pool of operations to manipulate dark matter data. The R76 dataset can be processed with the library.
Check out the [library guide](https://github.com/nsdf-fabric/nsdf-slac/blob/main/docs/library.md) for a step by step walkthrough.

### Library Usage Example

```python
from nsdf_dark_matter.idx import CDMS, load_all_data

# Loading the data from a valid idx structure
cdms = load_all_data('path/to/idx/dir')

# fetching all event ids
event_ids = cdms.get_event_ids()

# fetching the metadata for an event id
metadata = cdms.get_event_metadata("10000")

# or by referencing an event id from event ids
metadata = cdms.get_event_metadata(event_ids[0])

# fetching all detector ids
detector_ids = cdms.get_detector_ids()

# fetching channels associated with a detector id
channels = cdms.get_detector_channels("10000_0_Phonon_4096")

# or by referencing a detector id from detector ids
channels =  cdms.get_detector_channels(detector_ids[0])
```
