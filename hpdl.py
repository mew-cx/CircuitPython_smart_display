# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.0.4"
__repo__ = "https://github.com/mew-cx/CircuitPython_smart_display"

import board
import digitalio
import time
import microcontroller

#import mew_pinbus

#import busio
#import atexit
#import gc
#import sys

#############################################################################

class PinBus:
    def __init__(self, board_pins):
        self._pins = tuple([self._init_pin(i) for i in board_pins])
        self._value = 0

    def init_pin(self, board_pin):
        pin = digitalio.DigitalInOut(board_pin)
        pin.switch_to_output()
        return pin

    def deinit(self):
        [pin.deinit() for pin in self._pins]

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
    ADDR_BITS = 2
    DATA_BITS = 2 #7

    def __init__(self, addr_pins, data_pins, wr_pin):
        """comment"""
        if len(addr_pins) != self.ADDR_BITS:
            raise TypeError("addr_pins must have {} elements".format(self.ADDR_BITS))
        if len(data_pins) != self.DATA_BITS:
            raise TypeError("data_pins must have {} elements".format(self.DATA_BITS))

        self._addr_pins = PinBus(addr_pins)
        self._data_pins = PinBus(data_pins)

        self._wr_pin = digitalio.DigitalInOut(wr_pin)
        self._wr_pin.switch_to_output()

    def __enter__(self):
        return self

    def __exit__(self, a1, a2, a3):
        self.deinit()
        supress_exception = False       # supress exception in 'with'?
        return supress_exception

    def deinit(self):
        self._addr_pins.deinit()
        self._data_pins.deinit()
        self._wr_pin.deinit()

    def SetChar(self, addr, data):
        self._addr_pins.value = addr
        self._wr_pin.value = False
        self._data_pins.value = data
        self._wr_pin.value = True

    def SetMessage(self, msg):
        raise NotImplementedException()

#############################################################################

DATA_PINS = (
    microcontroller.pin.PA03,
    microcontroller.pin.PA05,
    #board.D1,
)

ADDR_PINS = (
    microcontroller.pin.PA22,
    microcontroller.pin.PA23,
)

WR_PIN = microcontroller.pin.PA07

a = HPDL1414(ADDR_PINS, DATA_PINS, WR_PIN)

print(a)
print(dir(a))
print(dir(a._addr_pins))
print(dir(a._data_pins))
a.SetChar(1, 0)
a.deinit()
print(__version__)
with HPDL1414(ADDR_PINS, DATA_PINS, WR_PIN) as b:
    b.SetChar(0, 2)
print("DONE")

#############################################################################
D0   wht microcontroller.pin.PA23	board.D12
D1   gry microcontroller.pin.PA21	board.D11
D2   vio microcontroller.pin.PA20	board.D10
D3   blu microcontroller.pin.PA19	board.D9
D4   brn microcontroller.pin.PA17	board.D1
D5   blk microcontroller.pin.PA16	board.D0
D6   grn microcontroller.pin.PA18	board.D7

A0   yel microcontroller.pin.PA15	board.D5
A1   ora microcontroller.pin.PA13	board.SCL

nWR  red microcontroller.pin.PA12	board.SDA

nCE1 grn microcontroller.pin.PA04	board.A4
nCE2 blu microcontroller.pin.PA06	board.A5

nCLR vio microcontroller.pin.PA01	board.SCK

nBL  blk microcontroller.pin.PA07	board.D2
CUE  gry microcontroller.pin.PA00	board.MOSI
nCU  wht microcontroller.pin.PB23	board.MISO
#############################################################################
