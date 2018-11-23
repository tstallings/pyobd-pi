#!/usr/bin/env python
from datetime import datetime
from obd_utils import scanSerial
import argparse
import logging
import os
import obd_io
import obd_sensors
import time
import traceback


class OBD_Recorder(object):

    def __init__(self, path, log_items):
        self.port = None
        self.sensorlist = []
        self.logger = logging.getLogger(self.__class__.__name__)
        now = datetime.now()
        filename = "{}/obd2_{}-{}-{}.log".format(
            path.rstrip("/"),
            str(now.year).zfill(2),
            str(now.month).zfill(2),
            str(now.day).zfill(2)
        )
        logging.basicConfig(level=logging.DEBUG, filename=filename)

        self.logger.info("Time, RPM, MPH, Throttle, Load, Fuel Status\n")

        for item in log_items:
            self.add_log_item(item)

        self.gear_ratios = [34/13, 39/21, 36/23, 27/20, 26/21, 25/22]

    def connect(self):
        portnames = scanSerial()
        self.logger.debug("portnames: {}".format(str(portnames)))
        for port in portnames:
            self.port = obd_io.OBDPort(port, None, 2, 2)
            if(self.port.State == 0):
                self.port.close()
                self.port = None
            else:
                break

        if(self.port):
            self.logger.debug("Connected to {}".format(self.port.port.name))

    def is_connected(self):
        return self.port

    def add_log_item(self, item):
        for index, e in enumerate(obd_sensors.SENSORS):
            if(item == e.shortname):
                self.sensorlist.append(index)
                self.logger.debug("Logging item: {}".format(e.name))
                break

    def record_data(self):

        if self.port is None:
            return None

        self.logger.debug("Logging started")

        try:
            while True:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S.%f")
                log_string = [current_time]
                results = {}
                for index in self.sensorlist:
                    (name, value, unit) = self.port.sensor(index)
                    log_string.append(str(value))
                    results[obd_sensors.SENSORS[index].shortname] = value

                # gear = self.calculate_gear(results["rpm"], results["speed"])
                self.logger.info(", ".join(log_string))
        except Exception as e:
            self.logger.exception(
                "Caught exception - [{}]: {}".format(
                    e.__class__.__name__,
                    str(e)
                )
            )

    def calculate_gear(self, rpm, speed):
        if speed == "" or speed == 0:
            return 0
        if rpm == "" or rpm == 0:
            return 0

        rps = rpm/60
        mps = (speed*1.609*1000)/3600

        primary_gear = 85/46  # street triple
        final_drive = 47/16

        tire_circumference = 1.978  # meters

        tire_revs_sec = float(rps * tire_circumference)
        gear_speed = float(mps * primary_gear * final_drive)  # gear speed?
        current_gear_ratio = tire_revs_sec / gear_speed

        self.logger.debug(
            "calculated gear ratio: {}".format(current_gear_ratio)
        )

        gear = min((abs(current_gear_ratio - i), i) for i in self.gear_ratios)
        return gear[1]


def main(args):
    logitems = ["rpm", "speed", "throttle_pos", "load", "fuel_status"]
    logger = logging.getLogger(__name__)
    o = OBD_Recorder(args.logfile, logitems)
    o.connect()

    while not o.is_connected():
        logger.debug("Not connected")
        time.sleep(2)

    logger.debug("Connected - staring recording!")
    o.record_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A utility for recording OBD2 messages"
    )
    parser.add_argument(
        "-f",
        "--logfile",
        action="store",
        required=False,
        default=os.path.expanduser("~"),
        help="Specify the filename for the capture"
    )
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        traceback.print_exc()
