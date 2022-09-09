# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.0.2"
__repo__ = "https://github.com/mew-cx/CircuitPython_smart_display"

import board
import digitalio
import time
#import mew_pinbus

#import busio
#import atexit
#import gc
#import sys

#############################################################################

class PinBus:
    def __init__(self, board_pins):
        self._pins = tuple([self._init_output_pin(i) for i in board_pins])
        self._value = 0

    def _init_output_pin(self, board_pin):
        pin = digitalio.DigitalInOut(board_pin)
        pin.switch_to_output(False, push-pull)
        return pin

    def deinit(self):
        [pin.deinit() for pin in self._pins]
        del self._pins

    @property
    def value(self):
        """Return the last value written to pins"""
        return self._value

    @value.setter
    def value(self, value):
        """Write value to the pins"""
        for pin in self._pins:
            pin.value = bool(value & 0x01)
            value >>= 1
        self._value = value

#############################################################################

class HPDL1414:
    DATA_BITS = 7
    ADDR_BITS = 2

    def __init__(self, data_pins, addr_pins, wr_pin):
        if len(data_pins) != self.DATA_BITS:
            raise TypeError("data_pins must have {} elements".format(self.DATA_BITS))
        if len(addr_pins) != self.ADDR_BITS:
            raise TypeError("addr_pins must have {} elements".format(self.ADDR_BITS))

        self._data_pins = PinBus(data_pins)
        self._addr_pins = PinBus(addr_pins)
        self._wr_pin = self.InitOutputPin(wr_pin)

    def __del__(self):
        del self._data_pins
        del self._addr_pins
        del self._wr_pin

    def __enter__(self):
        #raise NotImplementedException()
        return self

    def __exit__(self):
        #raise NotImplementedException()
        self.deinit()

    def deinit(self):
        self._data_pins.deinit()
        self._addr_pins.deinit()
        self._wr_pin.deinit()

    def InitOutputPin(self, board_pin):
        pin = digitalio.DigitalInOut(board_pin)
        pin.switch_to_output(False, push-pull)
        return pin

    def SetDataPins(self, value):
        self.SetPins(self.data_pins, value)

    def SetAddrPins(self, value):
        self.SetPins(self.addr_pins, value)

    def StrobeWrPin(self):
        self.wr_pin.value = True
        # delay?
        self.wr_pin.value = False

    def SetChar(self, data, addr):
        SetDataPins(data)
        SetAddrPins(addr)
        StrobeWrPin()

    def SetMessage(self, msg):
        raise NotImplementedException()

#############################################################################

DATA_PINS = (
    board.D0,
    board.D1,
    board.D2,
    board.D3,
    board.D4,
    board.D5,
    board.D6,
)

ADDR_PINS = (
    board.D7,
    board.D8,
)

WR_PIN = board.D9

a = HPDL1414(DATA_PINS, ADDR_PINS, WR_PIN)

print(a)
print(dir(a))
print(len(a.data_pins))
print(333)

#############################################################################

class SPS30_I2C(SPS30):
    @property
    def auto_cleaning_interval(self):
        """Read the auto cleaning interval."""
        self._sps30_command(self._CMD_RW_AUTO_CLEANING_INTERVAL, rx_size=6)
        self._buffer_check(6)
        self._scrunch_buffer(6)
        if self._delays:
            time.sleep(0.005)
        return unpack_from(">I", self._buffer)[0]

    @auto_cleaning_interval.setter
    def auto_cleaning_interval(self, value):
        """Write the auto cleaning interval in seconds to SPS30 nvram (0 disables feature).
