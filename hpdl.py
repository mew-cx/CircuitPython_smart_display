# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.0.1"
__repo__ = "https://github.com/mew-cx/CircuitPython_smart_display"

import board
import digitalio
import time

#import busio
#import atexit
#import gc
#import sys
#import micropython

#############################################################################

class HPDL1414:
    DATA_BITS = 7
    ADDR_BITS = 2

    def __init__(self, data_pins, addr_pins, wr_pin):
        if len(data_pins) != self.DATA_BITS:
            raise TypeError("data_pins must have {} elements".format(self.DATA_BITS))
        if len(addr_pins) != self.ADDR_BITS:
            raise TypeError("addr_pins must have {} elements".format(self.ADDR_BITS))

        self.data_pins = tuple(self.InitOutputPins(data_pins))
        self.addr_pins = tuple(self.InitOutputPins(addr_pins))
        self.wr_pin = self.InitOutputPin(wr_pin)

    def __del__(self):
        del self.data_pins
        del self.addr_pins
        del self.wr_pin

    def __enter__(self):
        raise NotImplementedException()

    def __exit__(self):
        raise NotImplementedException()

    def deinit(self):
        (pin.deinit() for pin in self.data_pins)
        (pin.deinit() for pin in self.addr_pins)
        self.wr_pin.deinit()

    def InitOutputPins(self, pins):
        return [self.InitOutputPin(i) for i in pins]

    def InitOutputPin(self, board_pin):
        pin = digitalio.DigitalInOut(board_pin)
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = False
        return pin

    def SetPins(self, iter, value):
        for pin in iter:
            pin.value = bool(value & 0x01)
            value >>= 1

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
