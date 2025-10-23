import os
import pytest
from nsdf_dark_matter.idx import load_all_data, EventMetadata, CDMS


@pytest.fixture(scope="class")
def setup_cdms(request):
    request.cls.event_metadata = EventMetadata()
    request.cls.cdms = CDMS()
    request.cls.cdms._load_from_dir(os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/idx/07180808_1558_F0001/")))
    request.cls.headers = ["event_id", "trigger_type", "readout_type", "global_timestamp"]
    request.cls.expected = {
        "eventID": "10000",
        "trigger_type": "Physics",
        "readout_type": "None",
        "global_timestamp": "Wednesday, August 08, 2018 08:58:03 PM UTC",
    }


@pytest.mark.usefixtures("setup_cdms")
class TestClassMethods:
    def test_event_metadata_extraction(self):
        metadata = ["10000", "Physics", "None", "1533761883"]
        self.event_metadata.extract(self.headers, metadata)

        assert self.event_metadata.trigger_type == self.expected["trigger_type"]
        assert self.event_metadata.readout_type == self.expected["readout_type"]
        assert self.event_metadata.global_timestamp == self.expected["global_timestamp"]

    def test_cdms_get_metadata(self):
        metadata = self.cdms.get_event_metadata("10000")
        assert metadata is not None
        assert metadata.trigger_type == self.expected["trigger_type"]
        assert metadata.readout_type == self.expected["readout_type"]
        assert metadata.global_timestamp == self.expected["global_timestamp"]

    def test_cdms_get_invalid_metadata(self):
        metadata = self.cdms.get_event_metadata("-1")
        assert metadata is None

    def test_cdms_get_detector_channels(self):
        channels = self.cdms.get_detector_channels("10000_0_Phonon_4096")
        assert channels is not None

    def test_cdms_get_invalid_detector_channels(self):
        channels = self.cdms.get_detector_channels("20000")
        assert len(channels) == 0

    def test_cdms_get_event_ids(self):
        event_ids = self.cdms.get_event_ids()
        assert event_ids is not None
        assert len(event_ids) != 0

    def test_cdms_get_detector_ids(self):
        detector_ids = self.cdms.get_detector_ids()
        assert detector_ids is not None
        assert len(detector_ids) != 0

    def test_cdms_get_detectors_by_event(self):
        detector_ids = self.cdms.get_detectors_by_event("10000")
        assert detector_ids is not None
        assert len(detector_ids) != 0

    def test_event_id_to_metadata_workflow(self):
        event_ids = self.cdms.get_event_ids()
        metadata = self.cdms.get_event_metadata(event_ids[0])
        assert metadata is not None
        assert metadata.trigger_type == self.expected["trigger_type"]
        assert metadata.readout_type == self.expected["readout_type"]
        assert metadata.global_timestamp == self.expected["global_timestamp"]

    def test_detector_id_to_channels_workflow(self):
        detector_ids = self.cdms.get_detector_ids()

        chan = self.cdms.get_detector_channels(detector_ids[0])
        assert len(chan) != 0
        assert len(chan) == 4
        assert len(chan[0]) == 4096

        chan2 = self.cdms.get_detector_channels(detector_ids[-1])
        assert len(chan2) != 0
        assert len(chan2) == 4
        assert len(chan2[0]) == 4096


class TestDataLoaderFunctions:
    def test_load_all_data(self):
        data = load_all_data(os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/idx/07180808_1558_F0001/")))
        assert data is not None
        assert data.channels is not None

        expected = {
            "eventID": "10000",
            "trigger_type": "Physics",
            "readout_type": "None",
            "global_timestamp": "Wednesday, August 08, 2018 08:58:03 PM UTC",
        }

        # event metadata
        metadata = data.get_event_metadata("10000")
        assert metadata.trigger_type == expected["trigger_type"]
        assert metadata.readout_type == expected["readout_type"]
        assert metadata.global_timestamp == expected["global_timestamp"]

        # detector channels
        channels = data.get_detector_channels("10000_0_Phonon_4096")
        assert channels is not None

        # detector ids
        detector_ids = data.get_detector_ids()
        assert detector_ids is not None
        assert len(detector_ids) != 0

        # event ids
        event_ids = data.get_event_ids()
        assert event_ids is not None
        assert len(event_ids) != 0
