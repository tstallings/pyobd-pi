#!/usr/bin/env python
from datetime import datetime
from obd_utils import scanSerial
import logging
import obd_io
import obd_sensors
import time


class OBD_Capture(object):

    def __init__(self):
        self.supportedSensorList = []
        self.port = None

    def connect(self):
        portnames = scanSerial()
        print portnames
        for port in portnames:
            self.port = obd_io.OBDPort(port, None, 2, 2)
            if(self.port.State == 0):
                self.port.close()
                self.port = None
            else:
                break

        if(self.port):
            print "Connected to "+self.port.port.name

    def is_connected(self):
        return self.port

    def getSupportedSensorList(self):
        return self.supportedSensorList

    def capture_data(self):

        text = ""
        # Find supported sensors - by getting PIDs from OBD
        # its a string of binary 01010101010101
        # 1 means the sensor is supported
        self.supp = self.port.sensor(0)[1]
        self.supportedSensorList = []
        self.unsupportedSensorList = []

        # loop through PIDs binary
        for i in range(0, len(self.supp)):
            if self.supp[i] == "1":
                # store index of sensor and sensor object
                self.supportedSensorList.append(
                    [i + 1, obd_sensors.SENSORS[i+1]]
                )
            else:
                self.unsupportedSensorList.append(
                    [i + 1, obd_sensors.SENSORS[i+1]]
                )

        for supportedSensor in self.supportedSensorList:
            text += "supported sensor index = {} {}".format(
                str(supportedSensor[0]),
                str(supportedSensor[1].shortname)
            )

        time.sleep(3)

        if(self.port is None):
            return None

        # Loop until Ctrl C is pressed
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S.%f")
        text = current_time + "\n"
        for supportedSensor in self.supportedSensorList:
            sensorIndex = supportedSensor[0]
            (name, value, unit) = self.port.sensor(sensorIndex)
            text += "{} = {} {}\n".format(name, value, unit)

        return text


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.debug("Initializing...")

    o = OBD_Capture()
    o.connect()
    time.sleep(3)

    while not o.is_connected():
        logger.debug("Not connected")

    while True:
        try:
            o.capture_data()
        except Exception as e:
            logger.exception(
                "Caught unhandled exception - [{}]: {}".format(
                    e.__class__.__name__,
                    str(e)
                )
            )
