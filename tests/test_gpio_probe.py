import subprocess
from unittest import TestCase
from unittest.mock import patch

from pktfwd.pktfwd_app import PktfwdApp
from pktfwd.utils import is_concentrator_sx1302, run_reset_lgw


class TestGPIOProbe(TestCase):
    @patch("pktfwd.utils.subprocess.run")
    def test_failed_reset_never_succeeds(self, run):
        run.side_effect = subprocess.CalledProcessError(1, ["reset", "stop"])
        with self.assertRaises(subprocess.CalledProcessError):
            run_reset_lgw("reset")
        run.assert_called_once_with(["reset", "stop"], check=True, timeout=10)

    @patch("pktfwd.utils.subprocess.run")
    def test_sensecap_or_reset_error_never_falls_back_to_sx1301(self, run):
        for required, output in [(True, "SPI failure"),
                                 (False, "ERROR: failed to reset SX1302")]:
            run.side_effect = subprocess.CalledProcessError(
                1, ["chip_id"], output=output)
            with self.assertRaises(RuntimeError):
                is_concentrator_sx1302("chip_id", "spidev0.0", required)
        run.side_effect = FileNotFoundError("chip_id")
        with self.assertRaises(FileNotFoundError):
            is_concentrator_sx1302("chip_id", "spidev0.0")

    @patch("pktfwd.pktfwd_app.is_concentrator_sx1302")
    @patch("pktfwd.pktfwd_app.PktfwdApp.prepare_to_start")
    @patch("pktfwd.pktfwd_app.update_global_conf")
    def test_sensecap_requires_sx1302(self, configure, prepare, probe):
        app = PktfwdApp("COMP-SENSECAPM1", None, "region", "sx1", "sx2",
                        None, None, None, "diag", 0, "reset", "chip_id", ".",
                        "forwarder", "sx1")
        probe.side_effect = RuntimeError("GPIO reset failed")
        with self.assertRaises(RuntimeError):
            app.start()
        probe.assert_called_once_with("chip_id", "spidev0.0",
                                      require_sx1302=True)
        configure.assert_not_called()
