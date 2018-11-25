import serial
import logging
logger = logging.getLogger("obd_utils")


def scanSerial():
    """scan for available ports. return a list of serial names"""
    available = []
    logger.debug("Scanning for bluetooth devices...")
    # Enable Bluetooh connection
    for i in range(10):
        try:
            s = serial.Serial("/dev/rfcomm{}".format(i))
            available.append((str(s.port)))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
        except Exception as e:
            logger.exception(
                "Failed to connect to comm port - [{}]: {}".format(
                    e.__class__.__name__,
                    str(e)
                )
            )

    # Enable USB connection
    logger.debug("Scanning for USB devices...")
    for i in range(256):
        try:
            s = serial.Serial("/dev/ttyUSB{}".format(i))
            available.append(s.portstr)
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
        except Exception as e:
            logger.exception(
                "Failed to connect to usb tty - [{}]: {}".format(
                    e.__class__.__name__,
                    str(e)
                )
            )

    # Enable obdsim
    logger.debug("Scanning for obdsim devices")
    for i in range(256):
        try:  # scan Simulator
            s = serial.Serial("/dev/pts/{}".format(i))
            available.append(s.portstr)
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
        except Exception as e:
            logger.exception(
                "Failed to connect to obdsim on pts device - [{}]: {}".format(
                    e.__class__.__name__,
                    str(e)
                )
            )

    return available
