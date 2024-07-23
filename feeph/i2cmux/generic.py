#!/usr/bin/env python3
"""
<...>

usage:
```
import busio
import feeph.i2c
import feeph.tca9548a


i2c_bus = busio.I2C(...)

with feeph.tca9548a.BurstHandler(i2c_bus=i2c_bus, i2c_adr=0x4C, channel_id=0) as bh:
    value = bh.read_register(register)
    bh.write_register(register, value + 1)
```
"""

import logging
import time

# module busio provides no type hints
import busio  # type: ignore
from feeph.i2c import BurstHandle, BurstHandler

LH = logging.getLogger("i2c")

# according to the datasheet multiple channels can be selected at the same time!
# -> www.ti.com/lit/ds/symlink/pca9548a.pdf (section 8.6.2 - Control Register)


class MuxBurstHandler(BurstHandler):
    """
    a short-lived I/O operation on the I²C bus

    Technically speaking this I/O operation could span multiple devices
    but we're making an design choice and assume a single device is being
    used. This simplifies the user interface.
    """

    def __init__(self, i2c_bus: busio.I2C, i2c_adr: int, tca_adr: int, tca_cid: int, timeout_ms: int | None):
        # this a low-level class and should not be used directly
        # specific implementations should be derive from this class and
        # they are expected to perform  all necessary input validation
        self._i2c_bus = i2c_bus
        self._i2c_adr = i2c_adr
        self._tca_adr = tca_adr
        self._tca_cid = tca_cid
        self._timeout_ms = timeout_ms

    def __enter__(self) -> BurstHandle:
        """
        Try to acquire a lock for exclusive access on the I²C bus.

        Raises a RuntimeError if it wasn't possible to acquire the lock
        within the given timeout.
        """
        LH.debug("[%d] Initializing an I²C I/O burst.", id(self))
        # 0.001         = 1 millisecond
        # 0.000_001     = 1 microsecond
        # 0.000_000_001 = 1 nanosecond
        self._timestart_ns = time.perf_counter_ns()
        sleep_time = 0.001  # 1 millisecond
        if self._timeout_ms is not None:
            timeout_ns = self._timeout_ms * 1000 * 1000
            deadline = time.monotonic_ns() + timeout_ns
            while not self._i2c_bus.try_lock():
                if time.monotonic_ns() <= deadline:
                    # I²C bus was busy, wait and retry
                    time.sleep(sleep_time)  # time is given in seconds
                else:
                    # unable to acquire the lock
                    raise RuntimeError("timed out before the I²C bus became available")
        else:
            while not self._i2c_bus.try_lock():
                # I²C bus was busy, wait and retry
                time.sleep(sleep_time)  # time is given in seconds
        # successfully acquired a lock
        # -----------------------------------------------------------------
        # send I²C command to configure the correct channel
        self.channel_switch = bytearray([1 << self._tca_cid])
        self._i2c_bus.writeto(self._tca_adr, self.channel_switch)
        # -----------------------------------------------------------------
        elapsed_ns = time.perf_counter_ns() - self._timestart_ns
        LH.debug("[%d] Acquired a lock on the I²C bus after %d ms.", id(self), elapsed_ns / (1000 * 1000))
        return BurstHandle(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr)

    def __exit__(self, exc_type, exc_value, exc_tb):
        elapsed_ns = time.perf_counter_ns() - self._timestart_ns
        LH.debug("[%d] I²C I/O burst completed after %d ms.", id(self), elapsed_ns / (1000 * 1000))
        # -----------------------------------------------------------------
        # send I²C command to reset the TCA9548A?
        self._i2c_bus.writeto(self._tca_adr, b"\x00")
        # -----------------------------------------------------------------
        LH.debug("[%d] Releasing the lock on the I²C bus.", id(self))
        self._i2c_bus.unlock()
