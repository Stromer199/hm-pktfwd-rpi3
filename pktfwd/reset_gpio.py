"""Reset Raspberry Pi concentrators using Debian bullseye's libgpiod 1.x.

Pins are controller offsets, never the kernel's dynamic sysfs GPIO numbers.
The Raspberry Pi kernel retains the final output-low state on line release.
Kernels configured with strict_gpiod/persist_gpio_outputs=n are unsupported:
they require a hardware reset pull-down or a driver that owns the line.
"""

import glob
import os
import sys
from time import sleep


PI_GPIO_LABELS = {"pinctrl-bcm2835", "pinctrl-bcm2711", "pinctrl-rp1"}
PULSE_SECONDS = 0.1


def reset_pins(arguments, environ):
    """Preserve the script's override > argument > environment precedence."""
    if len(arguments) not in (1, 2) or arguments[0] not in ("start", "stop"):
        raise ValueError("Usage: reset_lgw.sh {start|stop} [reset-pin]")
    primary = environ.get(
        "CONCENTRATOR_RESET_PIN_OVERRIDE",
        arguments[1] if len(arguments) == 2 else
        environ.get("CONCENTRATOR_RESET_PIN", ""))
    values = [primary]
    secondary = environ.get("SX125x_RESET_PIN_OVERRIDE",
                            environ.get("SX125x_RESET_PIN"))
    if secondary is not None:
        values.append(secondary)
    if any(not value.isdecimal() for value in values):
        raise ValueError("Reset pins must be non-negative controller offsets")
    pins = [int(value) for value in values]
    if len(set(pins)) != len(pins):
        raise ValueError("Concentrator and SX125x reset pins must be distinct")
    return pins


def find_gpio_chip(gpiod, pins, override=None):
    """Find the Pi GPIO controller by label, independent of gpiochip index."""
    paths = [override] if override else sorted(glob.glob("/dev/gpiochip*"))
    matches = []
    for path in paths:
        with gpiod.Chip(path) as chip:
            if chip.label() in PI_GPIO_LABELS:
                if max(pins) >= chip.num_lines():
                    raise ValueError("Reset offset is outside %s (%s lines)" %
                                     (path, chip.num_lines()))
                matches.append(path)
    if len(matches) != 1:
        raise RuntimeError(
            "Expected one Raspberry Pi GPIO controller, found %s; "
            "check /dev/gpiochip* access and CONCENTRATOR_GPIO_CHIP" %
            len(matches))
    return matches[0]


def pulse_reset(gpiod, chip_path, pins):
    """Hold exclusive ownership over the complete low/high/low sequence."""
    with gpiod.Chip(chip_path) as chip:
        lines = chip.get_lines(pins)
        values = [0] * len(pins)
        lines.request(consumer="helium-concentrator-reset",
                      type=gpiod.LINE_REQ_DIR_OUT, default_vals=values)
        try:
            sleep(PULSE_SECONDS)
            for index in range(len(pins)):
                values[index] = 1
                lines.set_values(values)
                sleep(PULSE_SECONDS)
                values[index] = 0
                lines.set_values(values)
                sleep(PULSE_SECONDS)
        finally:
            try:
                # Deassert reset even if a GPIO write fails during a pulse.
                lines.set_values([0] * len(pins))
            finally:
                lines.release()


def main():
    try:
        pins = reset_pins(sys.argv[1:], os.environ)
        import gpiod
        chip_path = find_gpio_chip(
            gpiod, pins, os.environ.get("CONCENTRATOR_GPIO_CHIP"))
        print("Concentrator reset via %s offsets %s" % (chip_path, pins),
              flush=True)
        pulse_reset(gpiod, chip_path, pins)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        print("ERROR: GPIO reset failed: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
