import logging
import os
import sys
import threading
import urllib.request

sys.path.append('../pythonUtils')
import TDateUtil as dateUtl

class Timelapse:   

    INTERVAL_TO_CAPTURE_IMG = 5
    CAPTURE_IMG_RETRIES = 3

    STATUS_OK = 0

    # STATUS DIRECTORY
    IS_WRITABLE = 1
    IS_DIRECTORY = 2
    IS_FILE = 3    
    # ERRORS DIRECTORY
    DIRECTORY_DO_NOT_EXIST = -1   
    IS_NOT_WRITABLE = -2

    # STATUS URLLIB
    # ...    
    # ERRORS URLLIB
    URLLIB_URL_ERROR = -20
    URLLIB_HTTP_ERROR = -21
    URLLIB_CONTENT_TOO_SHORT_ERROR = -22
 
    def __init__(self, directory, url):   
        self.logger = logging.getLogger(__name__)  
        self.logger.debug("Init, directory=" + directory + ", url=" + url)
        self.directory = directory     
        self.url = url
        self.timer = threading.Timer(Timelapse.INTERVAL_TO_CAPTURE_IMG, self.captureImage) 

        self.directoryInfo = self.isDirectory(self.directory)
        if(self.directoryInfo == Timelapse.IS_DIRECTORY):
            self.directoryInfo = self.isWritable(self.directory)
            if( self.directoryInfo == Timelapse.IS_WRITABLE):
                self.logger.debug("Directory exists and is writable = " + self.directory)
            else:
                self.logger.debug("Directory is not writable = " + self.directory)
        elif(self.directoryInfo == Timelapse.IS_FILE):
            self.logger.debug("Directory is a file = " + self.directory)
        elif(self.directoryInfo == Timelapse.DIRECTORY_DO_NOT_EXIST):            
            os.mkdir(self.directory)
            self.directoryInfo = Timelapse.IS_WRITABLE
            self.logger.debug("Directory created = " + self.directory)
        
        # The "output" folder is ok, now we need to start capturing images
        if(self.directoryInfo == Timelapse.IS_WRITABLE):         
            # A frame every 10min, so we'll have 10fph, 240fpd -> 1h of the day = 1s = 10 imgs   
            self.logger.debug("Timer started, interval=" + str(Timelapse.INTERVAL_TO_CAPTURE_IMG) + "s")
            self.timer.start() 
            
    def __del__(self):
        self.timer.cancel()
    
    def timerCancel(self):
        self.timer.cancel()

    def isDirectory(self, directory):
        if os.path.exists(directory):
            if os.path.isfile(directory):
                return Timelapse.IS_FILE
            else:
                return Timelapse.IS_DIRECTORY
        else:
            return Timelapse.DIRECTORY_DO_NOT_EXIST

    def isWritable(self, directory):
        if(os.access(directory, os.X_OK | os.W_OK) == True):
            return Timelapse.IS_WRITABLE
        else:
            return Timelapse.IS_NOT_WRITABLE

    def setUrl(self, url):
        self.url = url
        self.logger.debug("setUrl=" + self.url)
    
    def getUrl(self):
        return self.url

    def captureImage(self):
        # Create a folder YYYYMMDD for the day's pictures if no exists
        timestamp = dateUtl.getTimeStamp("%Y%m%d")
        self.directoryInfo = self.isDirectory(self.directory + "/" + timestamp)
        if(self.directoryInfo == Timelapse.DIRECTORY_DO_NOT_EXIST):
            os.mkdir(self.directory + "/" + timestamp)
            self.logger.debug("Directory created=" + self.directory + "/" + timestamp)
        # Set the image directory
        self.imageDirectory = self.directory + "/" + timestamp

        # Capture the image
        if(self.url == None or len(self.url) == 0):
            self.logger.error("URL is not set")
        else:
            for retry in range(Timelapse.CAPTURE_IMG_RETRIES):	
                try:
                    urllib.request.urlretrieve(self.url, self.imageDirectory + "/" + dateUtl.getTimeStamp("%Y%m%d%H%M%S") + ".jpg")
                    self.logger.debug("Image captured, retry=" + str(retry))
                    break
                except urllib.error.URLError as e:
                    self.logger.error("URLError=" + str(e))
                except urllib.error.HTTPError as e:
                    self.logger.error("HTTPError=" + str(e))
                except urllib.error.ContentTooShortError as e:
                    self.logger.error("ContentTooShortError=" + str(e))
                self.logger.warning("Capture Img retry " + str(retry+1) + "/" + str(Timelapse.CAPTURE_IMG_RETRIES))
        self.timer = threading.Timer(Timelapse.INTERVAL_TO_CAPTURE_IMG, self.captureImage)
        self.timer.start()

