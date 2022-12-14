# SPDX-FileCopyrightText: 2022 Michael E. Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.2.0"
__repo__ = "https://github.com/mew-cx/CircuitPython_smart_display"

import board
import digitalio
#from time import sleep
import time

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
        assert self._pin, "OutputPin already deinited."    # TODO type(self)
        self._pin.deinit()
        self._pin = None

#    @property
#    def value(self):
#        return 1 if self._pin.value else 0

#    @value.setter
    def _value_setter(self, value):
        self._pin.value = bool(value)

    value = property(lambda self: 1 if self._pin.value else 0,
            _value_setter, None,
            "TODO value docstring")

    def strobe(self, duration=0):
        "Flip pin state, wait a bit, then flip again to restore."
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
        self._max_value = (1 << self._len) - 1
        self._value = value
        plist = []
        for bpin in board_pins:
            plist.append(OutputPin(bpin, value & 0x01))
            value >>= 1
        self._pins = tuple(plist)

    def deinit(self):
        assert self._pins, "PinBus already deinited."   # TODO type(self)
        [pin.deinit() for pin in self._pins]
        self._pins = None
        self._len = 0
        self._max_value = 0

    def _value_setter(self, value):
        #print("PinBus setter(",value,")")
        assert self._pins, "object is deinited; create another."        # TODO type(self)
        assert 0 <= value <= self._max_value, "value is out of range."
        self._value = value
        for pin in self._pins:
            pin.value = value & 0x01
            #print("\t", pin.value)
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
        self._wr_pin    = OutputPin(wr_pin, 1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()
        # False = dont supress an exception occurring inside the context
        return False

    def deinit(self):
        #print(type(self), "deinit()")
        self._addr_pins.deinit()
        self._data_pins.deinit()
        self._wr_pin.deinit()

    def put(self, addr, data):
        "Put a single character at specified position"
        #print(type(self), "put(", addr, data, ")")
        assert 0 <= addr < self.NUM_CHARS, "addr is out of range."
        assert 32 <= data < 128, "data must be integer ascii code."
        self._addr_pins.value = addr
        self._data_pins.value = data
        self._wr_pin.strobe()

    def fill(self, data):
        for i in range(self.NUM_CHARS):
            self.put(i, data)

    def clear(self):
        self.fill(ord(" "))

    def print(self, msg):
        assert len(msg) <= self.NUM_CHARS, "msg is too long."
        for i,c in enumerate(msg):
            self.put((self.NUM_CHARS-1) - i, ord(c))
        #raise NotImplementedError()

#############################################################################

class HPDL2416(HPDL1414):
    """TODO"""
    CE_BITS = 2

    def __init__(self, addr_pins, data_pins, wr_pin, ce_pins, nclr_pin, nbl_pin, cue_pin, ncu_pin):
        """TODO"""
        if len(ce_pins) != self.CE_BITS:
            raise ValueError("ce_pins must have {} elements".format(self.CE_BITS))

        super().__init__(addr_pins, data_pins, wr_pin)
        self._ce_pins  = PinBus(ce_pins, 3)
        self._nclr_pin = OutputPin(nclr_pin, 1)
        self._nbl_pin  = OutputPin(nbl_pin, 1)
        self._cue_pin  = OutputPin(cue_pin, 0)
        self._ncu_pin  = OutputPin(ncu_pin, 1)

    def deinit(self):
        print(type(self), "deinit()")
        self._ce_pins.deinit()
        self._nclr_pin.deinit()
        self._nbl_pin.deinit()
        self._cue_pin.deinit()
        self._ncu_pin.deinit()
        super().deinit()

    def chip_enable(self, value):
        print(type(self), "chip_enable(", value, ")")
        self._ce_pins.value = value

    def clear(self):
        # per datasheet, hold nCLR low at least 4ms
        print(type(self), "clear()")
        self._nclr_pin.strobe(0.005)

    def blank(self, value):
        # nBL is inverted logic
        print(type(self), "blank(", value, ")")
        self._nbl_pin.value(not bool(value))

    def cursor_enable(self, value):
        print(type(self), "cursor_enable(", value, ")")
        self._cue_pin.value(bool(value))

    def cursor_mode(self, value):
        # nCU is inverted logic
        print(type(self), "cursor_mode(", value, ")")
        self._ncu_pin.value(not bool(value))

#############################################################################

import microcontroller

# ItsyBitsy M0
if False:
    ADDR_PINS = (
        microcontroller.pin.PA15,               # A0
        microcontroller.pin.PA13,               # A1
    )

    DATA_PINS = (
        microcontroller.pin.PA23,               # D0
        microcontroller.pin.PA21,               # D1
        microcontroller.pin.PA20,               # D2
        microcontroller.pin.PA19,               # D3
        microcontroller.pin.PA17,               # D4
        microcontroller.pin.PA16,               # D5
        microcontroller.pin.PA18,               # D6
    )

    WR_PIN = microcontroller.pin.PA12           # nWR red board.SDA

    CE_PINS = (
        microcontroller.pin.PA04,               # nCE1 grn board.A4
        microcontroller.pin.PA06,               # nCE2 blu board.A5
    )

    nCLR_PIN = microcontroller.pin.PA01         # nCLR vio board.SCK
    nBL_PIN  = microcontroller.pin.PA07         # nBL  blk board.D2
    CUE_PIN  = microcontroller.pin.PA00         # CUE  gry board.MOSI
    nCU_PIN  = microcontroller.pin.PB23         # nCU  wht board.MISO

# RasPi Pico
if True:
    ADDR_PINS = (
        board.GP4,      # yel
        board.GP3,      # ora
    )

    DATA_PINS = (
        board.GP9,      # wht
        board.GP8,      # gry
        board.GP7,      # vio
        board.GP6,      # blu
        board.GP1,      # brn
        board.GP0,      # blk
        board.GP5,      # grn
    )

    WR_PIN = board.GP2  # red

#############################################################################

def main():
    with HPDL1414(ADDR_PINS, DATA_PINS, WR_PIN) as a:
        a.fill(ord("!"))
        time.sleep(1)

        a.put(3, ord("3"))
        a.put(2, ord("2"))
        a.put(1, ord("1"))
        a.put(0, ord("0"))
        time.sleep(1)

        a.clear()
        time.sleep(1)

        a.print("ABCD")
        time.sleep(1)

#TODO    x = HPDL2416(ADDR_PINS, DATA_PINS, WR_PIN,
#        CE_PINS, nCLR_PIN, nBL_PIN, CUE_PIN, nCU_PIN)

    print(__version__)

main()

# eof
