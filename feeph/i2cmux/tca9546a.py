#!/usr/bin/env python3
"""
PCA9546A  & TCA9546A

datasheet:
  - https://www.ti.com/lit/ds/symlink/pca9546a.pdf
  - https://www.ti.com/lit/ds/symlink/tca9546a.pdf
"""

# module busio provides no type hints
import busio  # type: ignore
from feeph.i2cmux.generic import MuxBurstHandler


class TCA9546A(MuxBurstHandler):
    """
    4-channel 1.65- to 5.5-V I2C/SMBus switch with reset & voltage translation
    """

    def __init__(self, i2c_bus: busio.I2C, i2c_adr: int, tca_adr: int = 0x70, tca_cid: int = 0, timeout_ms: int | None = 500):
        if 0x00 <= i2c_adr <= 0x6F or 0x78 <= i2c_adr <= 0xFF:
            self._i2c_adr = i2c_adr
        else:
            raise ValueError("device address must be in range 0x00 ≤ x ≤ 0xFF (excluding 0x70..0x77)")
        if 0x70 <= tca_adr <= 0x77:
            self._tca_adr = tca_adr
        else:
            raise ValueError("TCA9548A address must be in range 0x70 ≤ x ≤ 0x77")
        if 0 <= tca_cid <= 3:
            self._tca_cid = tca_cid
        else:
            raise ValueError("TCA9548A channel id must be in range 0 ≤ x ≤ 3")
        if timeout_ms is None:
            self._timeout_ms = None
        elif isinstance(timeout_ms, int) and timeout_ms > 0:
            self._timeout_ms = timeout_ms
        else:
            raise ValueError("Provided timeout is not a positive integer or 'None'!")
        super().__init__(i2c_bus=i2c_bus, i2c_adr=i2c_adr, tca_adr=tca_adr, tca_cid=tca_cid, timeout_ms=timeout_ms)


class PCA9546A(TCA9546A):
    """
    4-channel 2.3- to 5.5-V I2C/SMBus switch with reset & voltage translation

    This model has been superseded by the TCA9546A.
    """
