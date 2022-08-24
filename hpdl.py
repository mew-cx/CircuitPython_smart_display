# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# hpdl.py

__version__ = "0.0.0.0"
__repo__ = "https://github.com/mew-cx/CircuitPython_hpdl.git"

import board

#import busio
#import time
#import atexit
import digitalio
#import gc
#import sys
#import micropython
#from micropython import const

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

#############################################################################

class HPDL1414:

    def __init__(self, data_pins, addr_pins, wr_pin):
        # confirm correct size of data_pins and addr_pins
        for i in range(len(args)):
            pin = digitalio.DigitalInOut(data_pins[i])
            pin.direction = digitalio.Direction.OUTPUT

class TheApp:
    "The top-level application code for the 'dust' weather station"

    def __init__(self):
        self.dots       = None          # string of dotstar LEDs
        self.ds1307     = None          # battery-backed real-time clock
        self.htu21d     = None          # humidity/temperature sensor
        self.mpl3115    = None          # barometric pressure sensor
        self.sps30      = None          # particulate matter sensor
        self.ipaddr     = None          # our IP address
        self.HOST       = const("pink") # syslog server name
        self.HOST       = const("192.168.1.159") # syslog server name
        self.PORT       = const(514)    # syslog server port
        self.NUM_DOTS   = const(4)      # how many LEDs in the dotstar string
        self.SLEEP_MINS = const(5)      # sleep between measurements [minutes]

    def SetDots(self, *args):
        if not len(args):
            self.dots.fill(0)
        else:
            for i in range(len(args)):
                self.dots[i] = args[i]

    def InitializeDevices(self):
        # SPI controls the 4-LED dotstar strip
        self.dots = adafruit_dotstar.DotStar(
            board.SCK, board.MOSI, self.NUM_DOTS, brightness=0.1)
        self.SetDots()

        # Turn off onboard D13 red LED to save power
        led = digitalio.DigitalInOut(board.LED)
        led.direction = digitalio.Direction.OUTPUT
        led.value = False

        # Turn off I2C VSENSOR to save power
        i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
        i2c_power.switch_to_input()

        # Turn off onboard NeoPixel to save power
        pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
        pixel.brightness = 0.0
        pixel.fill((0, 0, 0))
        # TODO disable board.NEOPIXEL_POWER

        # The SPS30 limits the I2C bus rate to maximum of 100kHz
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

        # Create the I2C sensor instances
        self.htu21d  = adafruit_htu21d.HTU21D(i2c)        # id 0x40
        self.mpl3115 = adafruit_mpl3115a2.MPL3115A2(i2c)  # id 0x60
        self.sps30   = SPS30_I2C(i2c, fp_mode=True)       # id 0x69

        # We only want barometric pressure, don't care about altitude.
        # mpl3115.sealevel_pressure = 101325

    def ConnectToAP(self):
        "Connect to wifi access point (AP) with our secret credentials"
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        self.ipaddr = wifi.radio.ipv4_address
        print("our ipaddr", self.ipaddr)

    def SocketToSyslog(self):
        pool = socketpool.SocketPool(wifi.radio)
        sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        sock.settimeout(5)      # [seconds]
        sock.connect((self.HOST, self.PORT))
        return sock

    def WriteToSyslog(self, sock, message, severity=rfc5424.Severity.INFO):
        syslog_msg = rfc5424.FormatSyslog(
            facility = rfc5424.Facility.LOCAL3,
            severity = severity,
            timestamp = rfc5424.FormatTimestamp(),
            hostname = self.ipaddr,
            app_name = "dust",
            msg = message)
        # TODO handle ECONNECT exception
        sock.send(syslog_msg)
        # HACK!!! Because we're not using SSL (required by rfc5424),
        # we need a linefeed to terminate the message.
        sock.send(b'\n')

    def AcquireData(self):

        ts = rfc5424.FormatTimestamp()

        h = "{:0.1f},{:0.1f},{:0.0f},".format(
            self.htu21d.temperature,
            self.htu21d.relative_humidity,
            self.mpl3115.pressure)

        x = self.sps30.read()
#        try:
#            x = self.sps30.read()
#        except RuntimeError as ex:
#            print("Cant read SPS30, skipping: " + str(ex))
#            continue

        p1 = "{:0.3f},".format(x["tps"])
        p2 = "{:0.1f},{:0.1f},{:0.1f},{:0.1f},".format(
            x["pm10 standard"], x["pm25 standard"], x["pm40 standard"], x["pm100 standard"])
        p3 = "{:0.0f},{:0.0f},{:0.0f},{:0.0f},{:0.0f}".format(
            x["particles 05um"], x["particles 10um"], x["particles 25um"],
            x["particles 40um"], x["particles 100um"])

        result = '"' + ts + '",' + h + p1 + p2 + p3
        return result

    def Sleep(self):
        for _ in range(self.SLEEP_MINS):
            time.sleep(60)              # [seconds]
            app.SetDots(0x008080, 0x008080)
            time.sleep(0.1)
            app.SetDots()

    def Shutdown(self):
#        self.WriteToSyslog(severity=rfc5424.Severity.NOTICE,
#            "TheApp.Shutdown")
        self.SetDots()
        # TODO what other shutdown tasks?

#############################################################################
# main


# vim: set sw=4 ts=8 et ic ai:
