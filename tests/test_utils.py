import tempfile
from unittest import TestCase
from pktfwd.utils import write_diagnostics, get_region_filename


class TestUtils(TestCase):
    def test_write_diagnotics_is_running(self):
        diagnostics_filepath = tempfile.mkstemp()[1]
        write_diagnostics(diagnostics_filepath, True)

        contents = open(diagnostics_filepath).read()
        self.assertEqual(contents, "true")

    def test_write_diagnotics_not_running(self):
        diagnostics_filepath = tempfile.mkstemp()[1]
        write_diagnostics(diagnostics_filepath, False)

        contents = open(diagnostics_filepath).read()
        self.assertEqual(contents, "false")

    def test_get_region_filename(self):
        self.assertEqual(get_region_filename("AS923_4"),
                         "AS923-4-global_conf.json")
        self.assertEqual(get_region_filename("EU868"),
                         "EU-global_conf.json")
        self.assertEqual(get_region_filename("US915"),
                         "US-global_conf.json")
