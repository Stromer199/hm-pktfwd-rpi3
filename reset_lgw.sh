#!/bin/sh

# Keep the ABI used by the Semtech chip-id and packet-forwarder binaries.
# Use Debian's interpreter with its matching python3-libgpiod package.
set -eu
SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
exec /usr/bin/python3 "$SCRIPT_DIR/pktfwd/reset_gpio.py" "$@"
