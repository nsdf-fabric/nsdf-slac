"""
idx dark matter lib
===================

This module offers a pool of operations that enable users to manipulate dark matter data.
"""

import csv
import os
from typing import List, DefaultDict, Union
from collections import defaultdict
from datetime import datetime, timezone
import numpy
import OpenVisus as ov


class EventMetadata:
    """EventMetadata stores all the metadata associated with a particular event

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

    def __str__(self):
        return f"Trigger Type: {self.trigger_type}, Readout Type: {self.readout_type}, Global Timestamp: {self.global_timestamp}"

    def extract(self, headers: List[str], metadata: List[str]):
        for i, h in enumerate(headers):
            metadata_header = h.strip()
            if metadata_header == "trigger_type":
                self.trigger_type = metadata[i].strip()
            elif metadata_header == "readout_type":
                self.readout_type = metadata[i].strip()
            elif metadata_header == "global_timestamp":
                dt = datetime.fromtimestamp(int(metadata[i].strip()), tz=timezone.utc)
                self.global_timestamp = dt.strftime("%A, %B %d, %Y %I:%M:%S %p UTC")
            else:
                continue


class CDMS:
    """CDMS class bundles all the data processed by the idx including the channel data, channel metadata map, and the event metadata map

    Attributes
    ----------
        channels: List
            All the channel data of an specific mid
        detector_ids: List[str]
            All the detector ids
        event_ids: List[str]
            All the event ids
        detector_to_bounds: DefaultDict[str, List]
            The mapping from detector to their associated bounds that give the position of the respective channels in the channels data
        event_to_metadata: DefaultDict[str, EventMetadata]
            The mapping from event ID to their associated metadata(trigger_type, readout_type, global_timestamp)

    Methods
    -------
        get_channels(): 
            Return all the channel data for all detectors across all events
        get_event_ids():
            Return all the event ids
        get detector_ids():
            Return all the detector ids
        get_detector_channels(detector_id):
            Returns all channel data associated with an specific detector_id
        get_event_metadata(event_id):
            Returns the metadata associated with an specific event id
    """

    def __init__(self):
        self.channels = []
        self.eventIDs: List[str] = []
        self.detectorIDs: List[str] = []
        self.detector_to_bounds: DefaultDict[str, List] = defaultdict(List)
        self.event_to_metadata: DefaultDict[str, EventMetadata] = defaultdict(
            EventMetadata
        )

    def _reset(self):
        self.channels = []
        self.eventIDs: List[str] = []
        self.detectorIDs: List[str] = []
        self.detector_to_bounds: DefaultDict[str, List] = defaultdict(List)
        self.event_to_metadata: DefaultDict[str, EventMetadata] = defaultdict(
            EventMetadata
        )

    def __str__(self):
        return f"channels: {len(self.channels)}, detector->bound: {len(self.detector_to_bounds)}, event->metadata: {len(self.event_to_metadata)}"

    def _load_from_dir(self, filepath: str):
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

        self._reset()

        for file in os.listdir(filepath):
            name = os.path.basename(file)
            if not os.path.isdir(name):
                sp = name.split(".")
                ext = sp[1] if len(sp) == 2 else ""
                if ext == "idx":
                    self.channels = _load_channel_data(os.path.join(filepath, name))
                elif ext == "csv":
                    self.event_to_metadata = _create_event_metadata_map(
                        os.path.join(filepath, name)
                    )
                    # set the list of all the event ids
                    for k in self.event_to_metadata.keys():
                        self.eventIDs.append(k)
                elif ext == "txt":
                    self.detector_to_bounds = _create_channel_metadata_map(
                        os.path.join(filepath, name)
                    )
                    # set the list of all detector ids
                    for k in self.detector_to_bounds.keys():
                        self.detectorIDs.append(k)
                else:
                    continue

    def get_event_ids(self) -> List[str]:
        """
        Returns all the event ids

        Returns
        -------
        List[str]
            A list containing all the event ids
        """
        return self.eventIDs

    def get_detector_ids(self) -> List[str]:
        """
        Returns all the detector ids

        Returns
        -------
        List[str]
            A list containing all the detector ids
        """
        return self.detectorIDs

    def get_channels(self):
        """
        Returns all the channel data for all detectors across all events

        Returns
        -------
        List
            A list of all channel data for all detectors across all events
        """

        return self.channels

    def get_detector_channels(self, detector_id: str):
        """
        Returns all the channel data associated with an specific detector id. A detector id is composed of the following
        <event_id>_<detector_number>_<type>_<channel_num>

        Parameters
        ----------
        detector_id
            The detector ID, i.e, 10000_0_Phonon_4096

        Returns
        -------
        List
            A list containing all the channels associated with the detector id. An empty list is returned if the provided detector ID is invalid
        """

        if detector_id not in self.detector_to_bounds:
            return []

        bounds = self.detector_to_bounds[detector_id]
        return self.channels[bounds[0]:bounds[1]]

    def get_event_metadata(self, event_id: str) -> Union[EventMetadata, None]:
        """
        Returns the metadata associated with an event

        Parameters
        ----------
        event_id: str
            The event ID, i.e, 10000

        Returns
        -------
        EventMetadata | None
            The EventMetadata object (trigger_type, readout_type, global_timestamp) or None if the provided ID is invalid
        """
        if event_id not in self.event_to_metadata:
            return None

        return self.event_to_metadata[event_id]

    def get_detectors_by_event(self, event_id: str) -> List[str]:
        """
        Returns all the detector ids for an specific event ID

        Parameters
        ----------
        event_id: str
            The event ID, i.e, 10000

        Returns
        -------
        List[str]
            A list containing all the detector ids associated with the event ID
        """
        detector_ids = []
        for k in self.detector_to_bounds.keys():
            if k.startswith(event_id):
                detector_ids.append(k)
        return detector_ids


#################################
### METADATA LOADER FUNCTIONS ###
#################################


def _create_channel_metadata_map(filepath: str) -> DefaultDict[str, List]:
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


def _create_event_metadata_map(filepath: str) -> DefaultDict[str, EventMetadata]:
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


def _load_channel_data(filepath: str) -> numpy.ndarray:
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
    return dataset  # type: ignore


def load_all_data(filepath: str) -> CDMS:
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
    data._load_from_dir(filepath)
    return data
