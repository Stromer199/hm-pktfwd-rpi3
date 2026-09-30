from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from pktfwd.reset_gpio import find_gpio_chip, pulse_reset, reset_pins


class TestResetGPIO(TestCase):
    def test_override_and_optional_pin_use_controller_offsets(self):
        environment = {"CONCENTRATOR_RESET_PIN": "38",
                       "CONCENTRATOR_RESET_PIN_OVERRIDE": "17",
                       "SX125x_RESET_PIN_OVERRIDE": "23"}
        self.assertEqual(reset_pins(["start", "22"], environment), [17, 23])
        self.assertEqual(reset_pins(["stop", "38"], {}), [38])
        with self.assertRaises(ValueError):
            reset_pins(["start"], {"CONCENTRATOR_RESET_PIN": ""})

    @patch("pktfwd.reset_gpio.glob.glob")
    def test_controller_discovery_does_not_assume_gpiochip_zero(self, glob):
        glob.return_value = ["/dev/gpiochip0", "/dev/gpiochip4"]
        expander, controller = MagicMock(), MagicMock()
        expander.label.return_value = "raspberrypi-exp-gpio"
        controller.label.return_value = "pinctrl-bcm2711"
        controller.num_lines.return_value = 58
        gpiod = MagicMock()
        gpiod.Chip.side_effect = [expander, controller]
        for chip in (expander, controller):
            chip.__enter__.return_value = chip
        self.assertEqual(find_gpio_chip(gpiod, [17]), "/dev/gpiochip4")
        expander.get_lines.assert_not_called()

    def test_unknown_controller_and_out_of_range_offset_fail(self):
        gpiod = MagicMock()
        chip = gpiod.Chip.return_value.__enter__.return_value
        chip.label.return_value = "raspberrypi-exp-gpio"
        with self.assertRaises(RuntimeError):
            find_gpio_chip(gpiod, [17], "/dev/gpiochip1")
        chip.label.return_value = "pinctrl-bcm2835"
        chip.num_lines.return_value = 54
        with self.assertRaises(ValueError):
            find_gpio_chip(gpiod, [529], "/dev/gpiochip0")

    @patch("pktfwd.reset_gpio.sleep")
    def test_pulses_hold_one_request_then_release_low(self, sleep):
        gpiod = MagicMock()
        lines = gpiod.Chip.return_value.__enter__().get_lines.return_value
        values = []
        lines.set_values.side_effect = lambda value: values.append(list(value))
        pulse_reset(gpiod, "/dev/gpiochip4", [17, 23])
        self.assertEqual(values, [[1, 0], [0, 0], [0, 1], [0, 0], [0, 0]])
        sleep.assert_has_calls([call(0.1)] * 5)
        lines.request.assert_called_once()
        lines.release.assert_called_once()

    @patch("pktfwd.reset_gpio.sleep")
    def test_failed_gpio_write_propagates_and_releases_line(self, sleep):
        gpiod = MagicMock()
        lines = gpiod.Chip.return_value.__enter__().get_lines.return_value
        lines.set_values.side_effect = [OSError("GPIO I/O failure"), None]
        with self.assertRaises(OSError):
            pulse_reset(gpiod, "/dev/gpiochip0", [17])
        lines.release.assert_called_once()
