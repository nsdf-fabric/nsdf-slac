import unittest
from nsdf_dark_matter.idx import load_all_data, EventMetadata, CDMS


class TestClassMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.event_metadata = EventMetadata()
        cls.cdms = CDMS()
        cls.cdms._load_from_dir("fixtures/idx/07180808_1558_F0001/")
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

    def test_cdms_get_metadata(self):
        metadata = self.cdms.get_event_metadata("10000")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.trigger_type, self.expected["trigger_type"])
        self.assertEqual(metadata.readout_type, self.expected["readout_type"])
        self.assertEqual(metadata.global_timestamp, self.expected["global_timestamp"])

    def test_cdms_get_invalid_metadata(self):
        metadata = self.cdms.get_event_metadata("-1")
        self.assertIsNone(metadata)

    def test_cdms_get_detector_channels(self):
        channels = self.cdms.get_detector_channels("10000_0_Phonon_4096")
        self.assertIsNotNone(channels)

    def test_cdms_get_invalid_detector_channels(self):
        channels = self.cdms.get_detector_channels("20000")
        self.assertTrue(len(channels) == 0)

    def test_cdms_get_event_ids(self):
        event_ids = self.cdms.get_event_ids()
        self.assertIsNotNone(event_ids)
        self.assertTrue(len(event_ids) != 0)

    def test_cdms_get_detector_ids(self):
        detector_ids = self.cdms.get_detector_ids()
        self.assertIsNotNone(detector_ids)
        self.assertTrue(len(detector_ids) != 0)

    def test_cdms_get_detectors_by_event(self):
        detector_ids = self.cdms.get_detectors_by_event("10000")
        self.assertIsNotNone(detector_ids)
        self.assertTrue(len(detector_ids) != 0)

    def test_event_id_to_metadata_workflow(self):
        event_ids = self.cdms.get_event_ids()
        metadata = self.cdms.get_event_metadata(event_ids[0])
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.trigger_type, self.expected["trigger_type"])
        self.assertEqual(metadata.readout_type, self.expected["readout_type"])
        self.assertEqual(metadata.global_timestamp, self.expected["global_timestamp"])

    def test_detector_id_to_channels_workflow(self):
        detector_ids = self.cdms.get_detector_ids()
        chan = self.cdms.get_detector_channels(detector_ids[0])
        self.assertTrue(len(chan) != 0)
        self.assertTrue(len(chan) == 4)
        self.assertTrue(len(chan[0]) == 4096)

        chan2 = self.cdms.get_detector_channels(detector_ids[-1])
        self.assertTrue(len(chan2) != 0)
        self.assertTrue(len(chan2) == 4)
        self.assertTrue(len(chan2[0]) == 4096)



class TestDataLoaderFunctions(unittest.TestCase):
    def test_load_all_data(self):
        data = load_all_data("fixtures/idx/07180808_1558_F0001/")
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.channels)
        expected = {
            "eventID": "10000",
            "trigger_type": "Physics",
            "readout_type": "None",
            "global_timestamp": "Wednesday, August 08, 2018 08:58:03 PM UTC",
        }

        # event metadata
        metadata = data.get_event_metadata("10000")
        self.assertEqual(metadata.trigger_type, expected["trigger_type"])
        self.assertEqual(metadata.readout_type, expected["readout_type"])
        self.assertEqual(metadata.global_timestamp, expected["global_timestamp"])

        # detector channels
        channels = data.get_detector_channels("10000_0_Phonon_4096")
        self.assertIsNotNone(channels)

        # detector ids
        detector_ids = data.get_detector_ids()
        self.assertIsNotNone(detector_ids)
        self.assertTrue(len(detector_ids) != 0)

        # event ids
        event_ids = data.get_event_ids()
        self.assertIsNotNone(event_ids)
        self.assertTrue(len(event_ids) != 0)


if __name__ == "__main__":
    unittest.main()
