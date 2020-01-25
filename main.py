import logging
from time import sleep
import sys
from TTimelapse import Timelapse
sys.path.append('../pythonUtils')
import TDateUtil as dateUtl

"""
    SET LOG SETTINGS
"""
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler("log/" + dateUtl.getTimeStamp("%Y%m%d") + ".log")
fh.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', '%m-%d-%Y %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
if(sys.argv[1] != "noconsole"):
    logger.addHandler(ch)
logger.debug("Logger configured")

if __name__ == "__main__":
    logger.debug("Program started")
    tl = Timelapse("output", "http://raspiwebcam.local:8081/?action=snapshot")
    print("Hit ^C to exit")
    while(True):
        try:
            sleep(1)
        except KeyboardInterrupt:
            tl.timerCancel()
            print("Exiting...")
            exit()
        
