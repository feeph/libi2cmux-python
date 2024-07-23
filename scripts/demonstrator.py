#!/usr/bin/env
"""
a sample script to show expected usage
(the defaults are suitable for a TCA9548A and EMC2101 on channel 0)

usage:
  pdm run scripts/demonstrator.py
"""

import argparse
import logging
import sys

# modules board and busio provide no type hints
import board  # type: ignore
import busio  # type: ignore

import feeph.i2cmux

LH = logging.getLogger("app")

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname).1s: %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(prog="demonstrator", description="demonstrate usage")
    parser.add_argument("-c", "--tca-channel", type=int, default=0)
    parser.add_argument("-m", "--tca-address", type=int, default=0x70)
    parser.add_argument("-a", "--device-address", type=int, default=0x4C)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        LH.setLevel(level=logging.DEBUG)

    i2c_bus = busio.I2C(scl=board.SCL, sda=board.SDA)

    i2c_adr = args.device_address
    tca_adr = args.tca_address
    tca_cid = args.tca_channel
    with feeph.i2cmux.TCA9548A(i2c_bus=i2c_bus, i2c_adr=i2c_adr, tca_adr=tca_adr, tca_cid=tca_cid) as bh:
        value = bh.read_register(0x00)
    LH.info("Register 0x00 has value 0x%02X", value)

    sys.exit(0)
