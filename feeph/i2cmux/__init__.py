#!/usr/bin/env python3
"""
multi-channel I²C bus multiplexers

This library is designed to serve as a drop-in replacement for 'feeph.i2c'
when an I²C bus multiplexer is being used.

product family
 - PCA9546A - 4-channel 2.3- to 5.5-V I2C/SMBus switch with reset & voltage translation
 - TCA9546A - 4-channel 1.65- to 5.5-V I2C/SMBus switch with reset & voltage translation
 - PCA9548A - 8-channel 2.3- to 5.5-V I2C/SMBus switch with reset & voltage translation
 - TCA9548A - 8-channel 1.65- to 5.5-V I2C/SMBus switch with reset & voltage translation

The PCA9546A and PCA9548A have been replaced by the TCA9546A and TCA9548A,
which offer an increased voltage range. Functionally they're identical.

usage:
```
import busio
import feeph.i2c_mux


i2c_bus = busio.I2C(...)

with feeph.i2c_mux.TCA9548A(i2c_bus=i2c_bus, i2c_adr=0x4C, tca_cid=0) as bh:
    value = bh.read_register(register)
    bh.write_register(register, value + 1)
```
"""

# the following imports are provided for user convenience
# flake8: noqa: F401
from feeph.i2cmux.tca9546a import PCA9546A, TCA9546A
from feeph.i2cmux.tca9548a import PCA9548A, TCA9548A
