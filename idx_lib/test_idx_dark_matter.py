import unittest
from idx_dark_matter import (
    create_channel_metadata_map,
    create_event_metadata_map,
    load_channel_data,
    load_all_data,
    EventMetadata,
    CDMS,
)


class TestMetadataFunctions(unittest.TestCase):

    def test_create_channel_metadata_map(self):
        detector_to_bounds = create_channel_metadata_map(
            "./idx/07180808_1558_F0001/07180808_1558_F0001.txt"
        )
        self.assertIn("10000_0_Phonon_4096", detector_to_bounds)
        self.assertEqual(len(detector_to_bounds["10000_0_Phonon_4096"]), 2)

    def test_create_event_metadata_map(self):
        event_metadata_map = create_event_metadata_map(
            "./idx/07180808_1558_F0001/07180808_1558_F0001.csv"
        )

        self.assertIn("10000", event_metadata_map)
        metadata = event_metadata_map["10000"]
        self.assertEqual(metadata.trigger_type, "Physics")
        self.assertEqual(metadata.readout_type, "None")
        self.assertEqual(
            metadata.global_timestamp,
            "Wednesday, August 08, 2018 08:58:03 PM UTC",
        )


class TestClassMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.event_metadata = EventMetadata()
        cls.cdms = CDMS()
        cls.cdms.load_from_dir("./idx/07180808_1558_F0001/")
        cls.headers = ["event_id", "trigger_type", "readout_type", "global_timestamp"]
        cls.expected = {
            "eventID": "10000",
            "trigger_type": "Physics",
            "readout_type": "None",
            "global_timestamp": "Wednesday, August 08, 2018 08:58:03 PM UTC",
        }

    def test_event_metadata_extraction(self):
        metadata = [
            "10000",
            "Physics",
            "None",
            "1533761883",
        ]
        self.event_metadata.extract(self.headers, metadata)
        self.assertEqual(
            self.event_metadata.trigger_type, self.expected["trigger_type"]
        )
        self.assertEqual(
            self.event_metadata.readout_type, self.expected["readout_type"]
        )
        self.assertEqual(
            self.event_metadata.global_timestamp, self.expected["global_timestamp"]
        )

    def test_cdms_metadata_loading(self):
        metadata = self.cdms.metadata_of("10000")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.trigger_type, self.expected["trigger_type"])
        self.assertEqual(metadata.readout_type, self.expected["readout_type"])
        self.assertEqual(metadata.global_timestamp, self.expected["global_timestamp"])

    def test_cdms_bounds_loading(self):
        [lo, hi] = self.cdms.bounds_of("10000_0_Phonon_4096")
        self.assertEqual(lo, 0)
        self.assertEqual(hi, 4)


class TestDataLoaderFunctions(unittest.TestCase):
    def test_load_channel_data(self):
        channel_data = load_channel_data(
            "./idx/07180808_1558_F0001/07180808_1558_F0001.idx"
        )
        self.assertIsNotNone(channel_data)

    def test_load_all_data(self):
        data = load_all_data("./idx/07180808_1558_F0001/")
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.channels)
        expected = {
            "eventID": "10000",
            "trigger_type": "Physics",
            "readout_type": "None",
            "global_timestamp": "Wednesday, August 08, 2018 08:58:03 PM UTC",
        }

        # event metadata
        metadata = data.metadata_of("10000")
        self.assertEqual(metadata.trigger_type, expected["trigger_type"])
        self.assertEqual(metadata.readout_type, expected["readout_type"])
        self.assertEqual(metadata.global_timestamp, expected["global_timestamp"])

        # detector->bounds mapping
        [lo, hi] = data.bounds_of("10000_0_Phonon_4096")
        self.assertEqual(lo, 0)
        self.assertEqual(hi, 4)


if __name__ == "__main__":
    unittest.main()
