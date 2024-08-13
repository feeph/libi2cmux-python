#!/usr/bin/env python3
"""
perform TCA9546A related tests

use simulated device:
  pdm run pytest
use hardware device:
  TEST_TCA9546A_CHIP=y pdm run pytest

It's possible to run the hardware tests using a TCA9548A instead of an
actual TCA9546A or PCA9546A.
"""

import os
import unittest

# modules board and busio provide no type hints
import board  # type: ignore
import busio  # type: ignore
from feeph.i2c import EmulatedI2C

import feeph.i2cmux as sut

if os.environ.get('TEST_TCA9546A_CHIP', 'n') == 'y':
    HAS_HARDWARE = True
else:
    HAS_HARDWARE = False


class TestComponent(unittest.TestCase):

    def setUp(self):
        self.i2c_adr = 0x70
        if HAS_HARDWARE:
            self.i2c_bus = busio.I2C(scl=board.SCL, sda=board.SDA)
        else:
            # initialize read/write registers
            registers = {}
            self.i2c_bus = EmulatedI2C(state={self.i2c_adr: registers})

    def tearDown(self):
        # nothing to do
        pass

    # ---------------------------------------------------------------------

    # selected channels are expressed as a bitmask
    #  0b0000_0000 - no channel is active
    #  0b0000_0001 - channel 0 is active
    #  0b0000_0010 - channel 1 is active
    #  0b0000_0100 - channel 2 is active
    #  0b0000_1000 - channel 3 is active

    def test_use_channel1(self):
        with sut.TCA9546A(i2c_bus=self.i2c_bus, i2c_adr=0x4C, tca_adr=0x70, tca_cid=0):
            computed = self.i2c_bus._state[0x70][-1]
        expected = 0x01  # channel 1 was selected
        self.assertEqual(computed, expected)

    def test_release_channel1(self):
        with sut.TCA9546A(i2c_bus=self.i2c_bus, i2c_adr=0x4C, tca_adr=0x70, tca_cid=0):
            pass
        computed = self.i2c_bus._state[0x70][-1]
        expected = 0x00  # no channel was selected
        self.assertEqual(computed, expected)

    def test_use_invalid_channel(self):
        self.assertRaises(ValueError, sut.TCA9546A, i2c_bus=self.i2c_bus, i2c_adr=0x4C, tca_adr=0x70, tca_cid=4)

    # ---------------------------------------------------------------------

    def test_multiplexed_device(self):
        state = {
            0x70: {
                -1: 0x00,
            },
            0x4C: {
                0x01: 0x12,
            }
        }
        i2c_bus = EmulatedI2C(state=state)
        with sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0x4C, tca_adr=0x70, tca_cid=0) as bh:
            computed = bh.read_register(0x01)
        expected = 0x12
        self.assertEqual(computed, expected)

    # ---------------------------------------------------------------------

    def test_invalid_device_address(self):
        # this code tests the equivalent of:
        # with sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0xFFFF) as bh:
        #     ...
        i2c_bus = EmulatedI2C(state={})
        # -----------------------------------------------------------------
        # -----------------------------------------------------------------
        self.assertRaises(ValueError, sut.TCA9546A, i2c_bus=i2c_bus, i2c_adr=0xFFFF)

    def test_invalid_tca_address(self):
        # this code tests the equivalent of:
        # with sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0x4C, tca_adr=0x07) as bh:
        #     ...
        i2c_bus = EmulatedI2C(state={})
        # -----------------------------------------------------------------
        # -----------------------------------------------------------------
        self.assertRaises(ValueError, sut.TCA9546A, i2c_bus=i2c_bus, i2c_adr=0x4C, tca_adr=0x07)

    def test_invalid_timeout(self):
        # this code tests the equivalent of:
        # with sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0x4C, timeout_ms=0) as bh:
        #     ...
        i2c_bus = EmulatedI2C(state={}, lock_chance=1)
        # -----------------------------------------------------------------
        # -----------------------------------------------------------------
        self.assertRaises(ValueError, sut.TCA9546A, i2c_bus=i2c_bus, i2c_adr=0x4C, timeout_ms=0)

    def test_hard_to_lock(self):
        state = {
            0x70: {
                -1: 0x00,
            },
            0x4C: {
                0x00: 0x12,
            },
        }
        i2c_bus = EmulatedI2C(state=state, lock_chance=1)
        # -----------------------------------------------------------------
        # simulating an extremely busy I²C bus
        # (there's a 1 percent chance to successfully lock the bus)
        with sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0x4C, timeout_ms=None) as bh:
            computed = bh.read_register(0x00)
        expected = 0x12
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_unable_to_lock(self):
        # this code tests the equivalent of:
        # with sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0x4C) as bh:
        #     ...
        i2c_bus = EmulatedI2C(state={}, lock_chance=0)  # impossible to acquire a lock
        bh = sut.TCA9546A(i2c_bus=i2c_bus, i2c_adr=0x4C)
        # -----------------------------------------------------------------
        # -----------------------------------------------------------------
        self.assertRaises(RuntimeError, bh.__enter__)
