# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.1.0"
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
    def __init__(self, board_pins, value=0):
        self._len = len(board_pins)
        self._max_value = 1 << self._len - 1
        self._value = value
        plist = []
        for board_pin in board_pins:
            pin = digitalio.DigitalInOut(board_pin)
            pin.switch_to_output(bool(value & 0x01))
            value >>= 1
            plist.append(pin)
        self._pins = tuple(plist)

    def deinit(self):
        if not self._pins:
            raise ValueError("object was deinited.  create another.")
        [pin.deinit() for pin in self._pins]
        self._pins = None
        self._len = 0
        self._max_value = 0

    len = property(lambda self: self._len)

    max_value = property(lambda self: self._max_value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """Write value to the pins"""
        self._value = value
        for pin in self._pins:
            pin.value = bool(value & 0x01)
            value >>= 1

#############################################################################

class HPDL1414:
    ADDR_BITS = 2
    DATA_BITS = 7

    def __init__(self, addr_pins, data_pins, wr_pin):
        """comment"""
        if len(addr_pins) != self.ADDR_BITS:
            raise ValueError("addr_pins must have {} elements".format(self.ADDR_BITS))
        if len(data_pins) != self.DATA_BITS:
            raise ValueError("data_pins must have {} elements".format(self.DATA_BITS))

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
        raise NotImplementedError()

#############################################################################

# ItsyBitsy M0
if False:
    DATA_PINS = (
        microcontroller.pin.PA23,
        microcontroller.pin.PA21,
        microcontroller.pin.PA20,
        microcontroller.pin.PA19,
        microcontroller.pin.PA17,
        microcontroller.pin.PA16,
        microcontroller.pin.PA18,
    )

    ADDR_PINS = (
        microcontroller.pin.PA15,
        microcontroller.pin.PA13,
    )

    WR_PIN = microcontroller.pin.PA12       # nWR red board.SDA


# RasPi Pico
if True:
    DATA_PINS = (
        board.GP0,
        board.GP1,
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
    )

    ADDR_PINS = (
        board.GP7,
        board.GP8,
    )

    WR_PIN = board.GP9


def main():
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
#nCE1 grn microcontroller.pin.PA04	board.A4
#nCE2 blu microcontroller.pin.PA06	board.A5
#
#nCLR vio microcontroller.pin.PA01	board.SCK
#
#nBL  blk microcontroller.pin.PA07	board.D2
#
#CUE  gry microcontroller.pin.PA00	board.MOSI
#nCU  wht microcontroller.pin.PB23	board.MISO
#############################################################################
