# hm-pktfwd
Helium Miner Packet Forwarder

This is a Python app that uses prebuilt utilities to detect the correct concentrator chip and region, then start the concentrator accordingly.

hm-pktfwd builds off three other repos which each built a portion of the code required to run the packet forwarder.

- [lora_gateway](https://github.com/NebraLtd/lora_gateway)
- [packet_forwarder](https://github.com/NebraLtd/packet_forwarder)
- [sx1302_hal](https://github.com/NebraLtd/sx1302_hal)

## reset_lgw.sh
`reset_lgw.sh` is a shared tool that is used on all concentrator chip versions.
On sx1301 chips, [its is recommended](https://github.com/NebraLtd/lora_gateway#31-reset_lgwsh) that the script is run before each time the concentrator is started.
On chips that use sx1302_hal, the reset script is [run automatically](https://github.com/NebraLtd/sx1302_hal/blob/3d73e6af43535f700ff7b6c2b49cc79d388cd70f/packet_forwarder/src/lora_pkt_fwd.c#L1656-L1662) when the concentrator starts and is expected to be located in the same directory as the `lora_pkt_fwd` module.

reset_lgw is used by all concentrators, and inspired by the [upstream](https://github.com/NebraLtd/lora_gateway/blob/971c52e3e0f953102c0b057c9fff9b1df8a84d66/reset_lgw.sh)
[versions](https://github.com/NebraLtd/sx1302_hal/blob/6324b7a568ee24dbd9c4da64df69169a22615311/tools/reset_lgw.sh).
That said, it is different from the originals, context specific to hm-pktfwd, and moved to this repo to avoid confusion about its intention.
Additional context [here](https://github.com/NebraLtd/sx1302_hal/pull/1#discussion_r733253225).

## Supported Region Plans

You can typically find the exact region plan you need to use at [What Helium Region](https://whatheliumregion.xyz/) or on the [Helium Miner GitHub repo](https://github.com/helium/miner/blob/master/priv/countries_reg_domains.csv) however the table below provides a rough guide...

| Region Plan | Region |
| --- | --- |
| AS923_1 | Most of Asia |
| AS923_2 | Vietnam and Indonesia |
| AS923_3 | Phillipines and Cuba |
| AS923_4 | Israel |
| AU915 | Australia, New Zealand and South America|
| CN470 | China |
| EU868 | Europe, Middle East and some of Africa |
| EU433 | Parts of Africa and Asia|
| IN865 | India and Pakistan |
| KR920 | South Korea |
| RU864 | Russia |
| US915 | North America |

Please note:
| Region Plan | Region |
| --- | --- |
| CN779 | NOT YET SUPPORTED |

## Customization

The following environment variables control various aspects of the program's operation.

|Variable|Default|Required|Description|
| --- | --- | --- | --- |
| VARIANT| - | Yes | [See variants](https://github.com/NebraLtd/hm-pyhelper/blob/f8b2d8ceb90cfcd1da658a73e3741cc6de2ff1ff/hm_pyhelper/hardware_definitions.py#L1) |
| SX1301_REGION_CONFIGS_DIR | - | Yes | Path to [sx1301 configs](https://github.com/NebraLtd/hm-pktfwd/tree/900925b5bb3eab6c51cdabe24a59fede3fc85fe5/pktfwd/config/lora_templates_sx1301) |
| SX1302_REGION_CONFIGS_DIR | - | Yes | Path to [sx1302 configs](https://github.com/NebraLtd/hm-pktfwd/tree/900925b5bb3eab6c51cdabe24a59fede3fc85fe5/pktfwd/config/lora_templates_sx1302) |
| UTIL_CHIP_ID_FILEPATH | - | Yes | Path to [chip_id](https://github.com/NebraLtd/sx1302_hal/tree/69811057222f6f9cf8929ebfdb7fc6e36cc2618d/util_chip_id |
| RESET_LGW_FILEPATH | - | Yes | Path to [reset.sh](https://github.com/NebraLtd/hm-pktfwd/blob/900925b5bb3eab6c51cdabe24a59fede3fc85fe5/reset_lgw.sh). The same file is used for all sx130x versions. |
| CONCENTRATOR_GPIO_CHIP | Auto-detected | No | Optional `/dev/gpiochipN` path. The controller must have a supported Raspberry Pi pinctrl label; the index is never assumed. |
| CONCENTRATOR_RESET_PIN_OVERRIDE | Variant RESET offset | No | Override the reset line's controller offset, not the dynamic sysfs GPIO number. SenseCAP M1 uses offset 17 on both balenaOS 6 and 8. |
| SX125x_RESET_PIN_OVERRIDE | Unset | No | Optional second reset line on the same controller. |
| PKTFWD_PUSH_TIMEOUT_MS | 20 | No | Integer 2–1000. Maximum nominal upstream ACK wait in milliseconds for the local multiplexer; a matching ACK returns immediately. |
| PKTFWD_AUTOQUIT_THRESHOLD | 6 | No | Integer 1–120. Restart after this many unanswered downstream keepalives so the multiplexer hostname is resolved again. |
| ROOT_DIR | - | Yes | Directory the app will be run from. Should be the same location. `global_conf.json` will also be copied here. |
| SX1302_LORA_PKT_FWD_FILEPATH | - | Yes | Path to built [sx1302 lora_pkt_fwd](https://github.com/NebraLtd/sx1302_hal/blob/69811057222f6f9cf8929ebfdb7fc6e36cc2618d/packet_forwarder/src/lora_pkt_fwd.c) executable. |
| SX1301_LORA_PKT_FWD_DIR | - | Yes | Directory that contains [sx1301 lora_pkt_fwd](https://github.com/NebraLtd/packet_forwarder/tree/e8f24fe37ba555e5ad1ddf8eed26d0136f30f8de/lora_pkt_fwd) executables for all SPI buses. |
| LORA_PKT_FWD_BEFORE_CHECK_SLEEP_SECONDS | 5 | No | Duration after starting lora_pkt_fwd before establishing if it started successfully. |
| LORA_PKT_FWD_AFTER_SUCCESS_SLEEP_SECONDS | 30 | No | Maximum diagnostics/region polling interval. A child process exit wakes the wait immediately. |
| LORA_PKT_FWD_AFTER_FAILURE_SLEEP_SECONDS | 2 | No | Duration to wait before restarting when concentrator exits with 0. If it exits with code greater than 0, program exits and container restarts. |
| LOGLEVEL | DEBUG | No | TRACE, DEBUG, INFO, WARN, etc. |
| REGION_FILEPATH | /var/pktfwd/region | No | Path where hm-miner [writes the region](https://github.com/NebraLtd/hm-miner/blob/8819d5439dc23b45a905ff126078aa59c5be3de8/gen-region.sh#L9). |
| DIAGNOSTICS_FILEPATH | /var/pktfwd/diagnostics | No | Process-alive indicator (`true`/`false`); it does not prove radio reception or upstream acceptance. |
| AWAIT_SYSTEM_SLEEP_SECONDS | 5 | No | How long [app sleeps](https://github.com/NebraLtd/hm-pktfwd/issues/63) before starting concentrator. |
| SENTRY_KEY | False | No | Key for Sentry. Sentry inactive if key is False. |
| REGION_OVERRIDE | False | No | Region override. eg `US915`. |
| BALENA_ID | From Balena | No | Only used with Sentry. |
| BALENA_APP_NAME | From Balena | No | Only used with Sentry. |

### GPIO compatibility and recovery

The reset path uses Linux GPIO character devices through Debian bullseye's
`python3-libgpiod` 1.x, invoked with `/usr/bin/python3`. It supports the Raspberry
Pi controllers labelled `pinctrl-bcm2835`, `pinctrl-bcm2711`, and `pinctrl-rp1`.
The deployed target fleets are SenseCAP M1 (Pi 4) and Nebra Indoor Gen 1 (Pi 3).
No sysfs GPIO writes or guessed global GPIO bases remain in this reset path.
Unknown/ambiguous controllers, busy lines, missing tools and reset I/O failures
stop startup with an error. SenseCAP M1 probe failures cannot select an SX1301
forwarder: this hardware uses SX1302/SX1303.

Each reset holds one exclusive line request across the original 100 ms
high/low pulses, then releases the lines low. This uses the Raspberry Pi
kernel's documented output persistence on release. The affected balenaOS 8
device was read back on 2026-09-30 with kernel 6.12.94-v8 and
`pinctrl_bcm2835.persist_gpio_outputs=Y`; its sysfs base was 512 while the GPIO
offset remained 17. A working balenaOS 6 device had base 0. Kernels configured
with `strict_gpiod` or `persist_gpio_outputs=n` need separate hardware/driver
validation before using this one-shot reset. Other board families are not
auto-detected by this backend. See the official
[Raspberry Pi GPIO guidance](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/A-history-of-GPIO-usage-on-Raspberry-Pi-devices-and-current-best-practices).

On Raspberry Pi kernel 6.1.77 the persistence parameter is absent: the
[GPIO free callback](https://github.com/raspberrypi/linux/blob/77fc1fbcb5c013329af9583307dd1ff3cd4752aa/drivers/pinctrl/bcm/pinctrl-bcm2835.c#L881)
preserves output mode unconditionally.

An old container killed during an update can leave its reset line owned by
`sysfs`. That export survives container exit, so the new character-device
request correctly reports a busy line. The following is a one-time operational
migration, owned by the fleet operator, only after the old packet-forwarder has
stopped and the new image reports this busy-line error. Run it in the new
packet-forwarder container. It validates the controller, runtime reset offsets
and `sysfs` consumer before unexporting only those lines. SenseCAP M1 uses
offset 17; Nebra Indoor Gen 1 uses offset 38 (unless explicitly overridden).
The example sets 17 explicitly because the app exports this variable only to
its own child processes; change it to 38 for Nebra Indoor Gen 1.
Other consumers must remain untouched. After this succeeds, restart the service
and verify radio reception and ACKs. No migration is needed again unless an old
sysfs-based release is rolled back into use; remove this procedure after those
rollback releases are retired.

```sh
CONCENTRATOR_RESET_PIN=17 /usr/bin/python3 - <<'PY'
import glob
import os
from pathlib import Path
import gpiod
from pktfwd.reset_gpio import find_gpio_chip, reset_pins

pins = reset_pins(["start"], os.environ)
device = find_gpio_chip(gpiod, pins, os.environ.get("CONCENTRATOR_GPIO_CHIP"))
with gpiod.Chip(device) as chip:
    controllers = [Path(path) for path in glob.glob("/sys/class/gpio/gpiochip*")
                   if (Path(path) / "label").read_text().strip() == chip.label()
                   and int((Path(path) / "ngpio").read_text()) == chip.num_lines()]
    if len(controllers) != 1:
        raise SystemExit("Ambiguous sysfs controller; no lines changed")
    base = int((controllers[0] / "base").read_text())
    for pin in pins:
        line = chip.get_line(pin)
        if line.consumer() != "sysfs":
            raise SystemExit("Reset line is not owned by sysfs; no lines changed")
        if not Path("/sys/class/gpio/gpio%d" % (base + pin)).is_dir():
            raise SystemExit("Missing exported reset line; no lines changed")
    for pin in pins:
        with open("/sys/class/gpio/unexport", "w") as unexport:
            unexport.write(str(base + pin))
        print("Released legacy reset export", base + pin, "on", device)
PY
```

The default six missed downstream keepalives trigger recovery in roughly one
minute with the existing 10-second keepalive interval, followed by process
restart and radio initialization. This recovers a stale multiplexer IP after a
container replacement. The Python supervisor wakes immediately when the child
exits instead of waiting out its 30-second diagnostics interval. Local templates
are rendered to runtime files without modifying the originals, including a
consistent gateway ID and recovery threshold in both SX1302 configuration files.
The upstream ACK timeout defaults to 20 ms instead of 100 ms because these
fleets send to a local multiplexer. When an ACK is absent, this bounds the
synchronous wait before the next radio receive fetch to nominally 20 ms,
reducing the previous bound by 80 ms. A matching ACK ends the wait immediately;
healthy traffic does not incur a fixed 20 ms sleep. Very late ACKs can be omitted
from ACK statistics. `PKTFWD_PUSH_TIMEOUT_MS` accepts integers from 2 to 1000;
the minimum avoids a zero socket timeout after the C forwarder halves it.
Regional channels, power limits and CRC filtering remain unchanged. Availability
and accepted traffic can improve; software cannot guarantee higher rewards.


## Building

### Source builds

This fork builds the packet forwarder and SX1302 HAL from the revisions pinned in
`vendor/`. Clone recursively so those sources are present in the Docker context:

```sh
git clone --recursive --branch repair/balenaos8-reliability https://github.com/Stromer199/hm-pktfwd-rpi3.git
cd hm-pktfwd-rpi3
git submodule update --init --recursive
```

The GitHub build workflow validates ARM64 images on pull requests and manual
runs. It does not publish images to the inherited Nebra registries. Deployments
use the source build configured in the corresponding `Stromer199/helium-*`
fleet repository; follow that repository's deployment instructions.

### Manual build

```sh
# Build and load the ARM64 image into the local Docker image store.
docker buildx build --platform linux/arm64/v8 --progress=plain --load -t hm-pktfwd:latest .

# Optionally stop at the Python dependency stage.
docker buildx build --platform linux/arm64/v8 --progress=plain --load --target pktfwd-builder -t pktfwd-builder .
```

### Testing

**Hardware Requirements:** An ARM64 based device.

**Software Requirements:**

* Docker ([instructions](https://docs.docker.com/engine/install/debian/))
* Docker Compose ([instructions](https://docs.docker.com/compose/install/))
* `git`

With the dependencies installed, do the following:

```
$ git clone --recursive --branch repair/balenaos8-reliability https://github.com/Stromer199/hm-pktfwd-rpi3.git
$ cd hm-pktfwd-rpi3
$ docker build . -t hm-pktfwd
```

Once you've built the image, we need to do a bit of prep work to mock the environment:

```
$ mkdir -p /var/pktfwd
$ echo region_eu868 | sudo tee -a /var/pktfwd/region
```

We're now finally ready to start up the containers using:

```
$ docker-compose up
```
