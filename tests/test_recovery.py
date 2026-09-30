import json
import os
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch

from pktfwd.utils import update_global_conf


class TestRecovery(TestCase):
    @patch("pktfwd.utils.get_ethernet_addresses")
    def test_configuration_renders_without_mutating_source_and_sets_recovery(
            self, get_addresses):
        get_addresses.side_effect = lambda addresses: addresses.update(
            E0="e4:5f:01:64:08:01")
        config = Path(__file__).resolve().parents[1] / "pktfwd" / "config"
        sources = [config / "lora_templates_sx1301",
                   config / "lora_templates_sx1302"]
        templates = [(source / "local_conf.json").read_text()
                     for source in sources]
        with tempfile.TemporaryDirectory() as directory:
            for is_sx1302 in (False, True):
                with patch.dict(os.environ,
                                {"PKTFWD_AUTOQUIT_THRESHOLD": "9",
                                 "PKTFWD_PUSH_TIMEOUT_MS": "12"}):
                    update_global_conf(is_sx1302, directory, *sources,
                                       "EU868", "spidev0.0")
                local = json.loads((Path(directory) / "local_conf.json")
                                   .read_text())
                self.assertEqual(local['gateway_conf']['gateway_ID'],
                                 "0000e45f01640801")
                self.assertEqual(
                    local['gateway_conf']['autoquit_threshold'], 9)
                self.assertEqual(local['gateway_conf']['push_timeout_ms'], 12)
                if is_sx1302:
                    global_conf = json.loads(
                        (Path(directory) / "global_conf.json").read_text())
                    self.assertEqual(global_conf['gateway_conf'],
                                     local['gateway_conf'])
            self.assertEqual([(source / "local_conf.json").read_text()
                              for source in sources], templates)
            with patch.dict(os.environ, {"PKTFWD_AUTOQUIT_THRESHOLD": "0"}):
                with self.assertRaises(ValueError):
                    update_global_conf(True, directory, *sources,
                                       "EU868", "spidev0.0")
            with patch.dict(os.environ, {}, clear=True):
                update_global_conf(True, directory, *sources,
                                   "EU868", "spidev0.0")
                rendered = json.loads(
                    (Path(directory) / "global_conf.json").read_text())
                self.assertEqual(rendered['gateway_conf']['push_timeout_ms'],
                                 20)
                for invalid in ("1", "1001", "2.5"):
                    os.environ["PKTFWD_PUSH_TIMEOUT_MS"] = invalid
                    with self.assertRaises(ValueError):
                        update_global_conf(True, directory, *sources,
                                           "EU868", "spidev0.0")
