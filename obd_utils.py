import serial
import logging
import subprocess
import os
import psutil
logger = logging.getLogger("obd_utils")


def find_obdsim():
    files = ["/dev/pts/{}".format(x) for x in os.listdir("/dev/pts/")]
    mappings = {}
    for f in files:
        try:
            out = subprocess.check_output(['lsof', '+wt', f])
            logger.debug("Got results for {}".format(f))
            mappings[f] = out
        except Exception as e:
            pass
            logger.error("[{}]: {}".format(e.__class__.__name__, str(e)))

    for k,v in mappings.items():
        lines = v.strip().split('\n')
        for line in lines:
            try:
                line = int(line)
                pname = psutil.Process(line).name()
                logger.debug("{}({}): {}".format(k, line, pname))
                if pname == "obdsim":
                    pts_dev = int(k.split(os.path.sep)[-1])
                    pts_path = "/dev/pts/{}".format(pts_dev + 1)
                    logger.debug("Found simulator on {}".format(pts_path))
                    return pts_path
            except Exception:
                pass


def scanSerial():
    """scan for available ports. return a list of serial names"""
    available = []
    logger.debug("Scanning for bluetooth devices...")
    # Enable Bluetooh connection
    for i in range(10):
        try:
            s = serial.Serial("/dev/rfcomm{}".format(i))
            available.append((str(s.port)))
            s.close()
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
            s.close()
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
    try:
        obdsim = find_obdsim()
        s = serial.Serial(obdsim)
        available.append(s.portstr)
        s.close()
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
