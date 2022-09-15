# SPDX-FileCopyrightText: 2022 Michael E. Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.1.1"
__repo__ = "https://github.com/mew-cx/CircuitPython_smart_display"

import board
import digitalio
from time import sleep

#import mew_pinbus

#import busio
#import atexit
#import gc
#import sys

#############################################################################

class OutputPin:
    """TODO"""
    def __init__(self, board_pin, value=0):
        self._pin = digitalio.DigitalInOut(board_pin)
        self._pin.switch_to_output(bool(value))

    def deinit(self):
        assert self._pin, "object already deinited."    # TODO type(self)
        self._pin.deinit()
        self._pin = None

    value = property(lambda self: 1 if self._pin.value else 0,
            lambda self, value: self._pin.value = bool(value),
            None,
            "TODO value docstring")

    def strobe(self, duration=0):
        assert self._pin, "object is deinited; create another." # TODO type(self)
        self._pin.value = not self._pin.value
        if duration:
            time.sleep(duration)
        self._pin.value = not self._pin.value

#############################################################################

class PinBus:
    """TODO"""
    def __init__(self, board_pins, value=0):
        self._len = len(board_pins)
        self._max_value = 1 << self._len - 1
        self._value = value
        plist = []
        for bpin in board_pins:
            plist.append(OutputPin(bpin, (value & 0x01)))
            value >>= 1
        self._pins = tuple(plist)

    def deinit(self):
        assert self._pins, "object already deinited."   # TODO type(self)
        [pin.deinit() for pin in self._pins]
        self._pins = None
        self._len = 0
        self._max_value = 0

    def _value_setter(self, value):
        assert self._pins, "object is deinited; create another."        # TODO type(self)
        assert 0 <= value <= self._max_value, "value is out of range."
        self._value = value
        for pin in self._pins:
            pin.value = value & 0x01
            value >>= 1

    value = property(lambda self: self._value, _value_setter, None,
            "TODO value docstring")

    len = property(lambda self: self._len, None, None,
            "TODO len docstring")

    max_value = property(lambda self: self._max_value, None, None,
            "TODO max_value docstring")

#############################################################################

class HPDL1414:
    """TODO"""
    ADDR_BITS = 2
    DATA_BITS = 7
    NUM_CHARS = 4

    def __init__(self, addr_pins, data_pins, wr_pin):
        """TODO"""
        if len(addr_pins) != self.ADDR_BITS:
            raise ValueError("addr_pins must have {} elements".format(self.ADDR_BITS))
        if len(data_pins) != self.DATA_BITS:
            raise ValueError("data_pins must have {} elements".format(self.DATA_BITS))

        self._addr_pins = PinBus(addr_pins)
        self._data_pins = PinBus(data_pins)
        self._wr_pin = OutputPin(wr_pin, 1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()
        # do not supress an exception occurring inside the context...
        return False

    def deinit(self):
        print("deinit")
        self._addr_pins.deinit()
        self._data_pins.deinit()
        self._wr_pin.deinit()

    def put(self, addr, data):
        print("put", addr, data)
        self._addr_pins.value = addr
        self._data_pins.value = data
        self._wr_pin.strobe()

    def fill(self, value):
        print("fill", value)
        for i in range(NUM_CHARS):
            put(i, value)

    def print(self, msg):
        print("print", msg)
        assert len(msg) <= 4, "msg is too long."
        for i,c in enumerate(msg):
            put(NUM_CHARS - i - 1, ord(c))
        #raise NotImplementedError()

#############################################################################
#class HPDL2416:
#    """TODO"""
# TODO list of CE values in order
#############################################################################

import microcontroller

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
    a.SetChar(1, 0)
    a.deinit()
    print(__version__)
    with HPDL1414(ADDR_PINS, DATA_PINS, WR_PIN) as b:
        b.SetChar(0, 2)
    print("DONE")

main()

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
