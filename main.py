import logging
import configparser
import os
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
fh = logging.FileHandler("log/timelapse_" + dateUtl.getTimeStamp("%Y-%m") + ".log")
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
logger.addHandler(ch)
if(len(sys.argv) > 1):
    if(sys.argv[1] == "noconsole"):
        logger.removeHandler(ch)
logger.debug("Logger configured")

"""
    INI SETTINGS
"""
if(os.path.exists("timelapse.ini")):
    logger.debug("timelapse.ini exists")
else:
    config = configparser.ConfigParser()
    config['TIMELAPSE'] = {'time_to_timelapse': '01:00:00',
                           'interval_to_capture_img': '120',
                           'capture_img_retries': '3',
                           'ffmpeg_process_timeout': '600'}
    # if using twitter to post timelapse, set to True and give the credentials                           
    config['TWITTER'] = {'enabled': 'False',
                         'consumer_key': '',
                         'consumer_secret': '',
                         'access_token': '',
                         'access_token_secret': ''}
    with open('timelapse.ini', 'w') as configfile:
        config.write(configfile)
    logger.debug("timelapse.ini not found, created with default values")

if __name__ == "__main__":
    logger.debug("Program started")
    tl = Timelapse("output", "http://raspiwebcam.local:8081/?action=snapshot")
    print("Hit ^C to exit")
    while(True):
        try:
            sleep(1)
            tl.runPendingSchedules()
        except KeyboardInterrupt:
            print("Timelapse sttoped")
            break
    del tl
    print("Exiting...")
    exit()   