"""
idx dark matter lib

This module provides multiple functions to manipulate the idx data format for SCDMS data.

* METADATA LOADER FUNCTIONS
    - create_channel_metadata_map
    - create_event_metadata_map

* CHANNEL DATA LOADER FUNCTIONS
    - load_channel_data
    - load_all_data
"""

import csv
import os
import numpy
import OpenVisus as ov
from typing import List, DefaultDict, Union
from collections import defaultdict
from datetime import datetime, timezone

class EventMetadata:
    """EventMetadata class to store all the metadata associated with a particular event

    Attributes
    ----------
        trigger_type: str 
            the trigger type (Physics, Unknown, etc)
        readout_type: str
            the readout type of the detector
        global_timestamp: str
            the global timestamp when the data was recorded
    """
    def __init__(self):
        self.trigger_type = "Unknown"
        self.readout_type = "None"
        self.global_timestamp = "None"

    def extract(self, headers: List[str], metadata: List[str]):
        for i, h in enumerate(headers):
            match h.strip():
                case "trigger_type":
                    self.trigger_type = metadata[i].strip()
                case "readout_type":
                    self.readout_type = metadata[i].strip()
                case "global_timestamp":
                    dt = datetime.fromtimestamp(int(metadata[i].strip()), tz=timezone.utc)
                    self.global_timestamp = dt.strftime('%A, %B %d, %Y %I:%M:%S %p UTC')
                case _:
                    continue


class CDMS:
    """CDMS class bundles all the data processed by the idx including the channel data, channel metadata map, and the event metadata map

    Attributes
    ----------
        channels: List
            All the channel data of an specific mid
        detector_to_bounds: DefaultDict[str, List]
            The mapping from detector to their associated bounds that give the position of the respective channels in the channels data
        event_to_metadata: DefaultDict[str, EventMetadata]
            The mapping from event ID to their associated metadata(trigger_type, readout_type, global_timestamp)
    """
    def __init__(self):
        self.channels = []
        self.detector_to_bounds: DefaultDict[str, List] = defaultdict(List)
        self.event_to_metadata: DefaultDict[str, EventMetadata] = defaultdict(EventMetadata)

    def __str__(self):
        return f"channels: {len(self.channels)}, detector->bound: {len(self.detector_to_bounds)}, event->metadata: {len(self.event_to_metadata)}"

    def load_from_dir(self, filepath: str):
        """
        Loads all CDMS data from a directory of processed data.
        NOTE: when loading the data of all processed files, the directory that contains the idx must be organized as follows

        dir/
        |-- mid_id/
        |   |-- 0000.bin
        |-- mid_id.idx
        |-- mid_id.csv
        |-- mid_id.txt
        """
        
        for file in os.listdir(filepath):
            name = os.path.basename(file)
            if not os.path.isdir(name):
                sp = name.split(".")
                ext = sp[1] if len(sp) == 2 else ""
                match ext:
                    case "idx":
                        self.channels = load_channel_data(os.path.join(filepath, name))
                    case "csv":
                        self.event_to_metadata = create_event_metadata_map(os.path.join(filepath, name))
                    case "txt":
                        self.detector_to_bounds = create_channel_metadata_map(os.path.join(filepath, name))
                    case _:
                        continue

    def bounds_of(self, detector_name: str) -> List[int]:
        """
        Return the bounds of the channels associated with a detector

        Parameters
        ----------
        detector_name: str
            The name of the detector to retrieve channels, i.e, 10000_0_Phonon_4096, detector 0 of event 10000

        Returns
        -------
        List
            A list of two values [lo,hi] denoting the bounds of the channel data associated with the detector
        """
        if detector_name in self.detector_to_bounds:
            return self.detector_to_bounds[detector_name]
        return []
    
    def metadata_of(self, event_id: str) -> Union[EventMetadata, None]:
        """
        Return the metadata associated with an event

        Parameters
        ----------
        detector_name: str
            The name of the detector to retrieve channels, i.e, 10000_0_Phonon_4096, detector 0 of event 10000

        Returns
        -------
        List
            A list of channel data associated with the detector
        """
        if event_id in self.event_to_metadata:
            return self.event_to_metadata[event_id]
        return None

#################################
### METADATA LOADER FUNCTIONS ###
#################################

def create_channel_metadata_map(filepath: str) -> DefaultDict[str, List]:
    """
    Creates the channel metadata map from a channel metadata file (mid_id.txt).

    This creates the detector to channel dictionary, i.e, 10000_0_Phonon_4096 refers to detector number 0 of event ID 10000.
    The entry on the dictionary would be as follows detector_to_bounds[10000_0_Phonon_4096] = [0,4] where the channels associated to detector number 0 of event ID 10000 are located in rows [0-4) of the channel data.

    Parameters
    ----------
    filepath: str
        The filepath to the channels metadata file, i.e, dir1/dir2/07180808_1558_F0001.txt

    Returns
    -------
    DefaultDict[str, List]
        The dictionary associating detectors with the bounds [lo,hi) where its channels are located
    """
    detector_to_bounds = defaultdict(list)
    with open(filepath, "r") as f:
        for line in f:
            detector_name, lo, hi = line.split(" ")
            detector_to_bounds[detector_name].append(int(lo))
            detector_to_bounds[detector_name].append(int(hi))
    f.close()
    return detector_to_bounds


def create_event_metadata_map(filepath: str) -> DefaultDict[str, EventMetadata]:
    """
    Creates the event metadata map from a event metadata file (mid_id.csv).
    Event metadata includes: Trigger Type, Readout Type, Global Timestamp

    Parameters
    ----------
    filepath: str
        The filepath to the event metadata file. i.e, dir1/dir2/07180808_1558_F0001.csv

    Returns
    -------
    DefaultDict[str, EventMetadata]
        The dictionary associating an event with its metadata.
    """

    mp = defaultdict(EventMetadata)
    i = 0
    headers = []
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        for line in reader:
            if i == 0:
                headers = line
            else:
                evt_metadata = EventMetadata()
                evt_metadata.extract(headers, line)
                mp[line[0]] = evt_metadata
            i += 1
    f.close()
    return mp

#############################
### DATA LOADER FUNCTIONS ###
#############################

def load_channel_data(filepath: str) -> numpy.ndarray:
    """
    Loads the channels data from an idx file. Usually is used in conjunction with create_channel_metadata_map to map detector to channels
    NOTE: when reading idx files the directory that contains the idx must be organized as follows

    dir/
    |-- mid_id/
    |   |-- 0000.bin
    |-- mid_id.idx

    Parameters
    ----------
    filepath: str
        The filepath to the idx file. i.e, dir1/dir2/07180808_1558_F0001.idx

    Returns
    -------
    List
        A list of channels data
    """

    dataset = ov.LoadDataset(filepath).read(field="data")
    return dataset # type: ignore

def load_all_data(filepath:str) -> CDMS:
    """
    Returns the CDMS object that contains: channel data, channel metadata, and event metadata.
    NOTE: when loading the data of all processed files, the directory that contains the idx must be organized as follows

    dir/
    |-- mid_id/
    |   |-- 0000.bin
    |-- mid_id.idx
    |-- mid_id.csv
    |-- mid_id.txt

    Parameters
    ----------
    filepath
        The filepath to the directory with all the processed files

    Returns
    -------
    CMDS
        The object that contains all the data from the processed files
    """

    data = CDMS()
    data.load_from_dir(filepath)
    return data

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        print(load_all_data(sys.argv[1]))
