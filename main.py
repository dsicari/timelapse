import logging
import logging.config
#logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Formatter = 2020-01-22 21:47:12.172 - __main__ - DEBUG - debug message
formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s")
# Log to file
filehandler = logging.FileHandler("log/log.txt")
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)
# Log to stdout too
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)

from TTimelapse import Timelapse
logger.debug("teste")
tl = Timelapse("output", "http://raspiwebcam.local:8081/?action=snapshot")