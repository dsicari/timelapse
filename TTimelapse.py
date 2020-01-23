import logging
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

import os
import sys
import threading
import urllib.request

sys.path.append('../pythonUtils')
import TDateUtil as dateUtl

class Timelapse:   

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

    def __init__(self, directory, verbose=False):   
        self.logger = logging.getLogger(__name__)   
        self.logger.setLevel(logging.DEBUG)  
        logger.debug("resss")
        logger.info(dateUtl.getDateTime())
        self.directory = directory
        self.verbose = verbose        
        self.url = "" # Need to call setUrl...

        self.directoryInfo = self.isDirectory(self.directory)

        if(self.directoryInfo == Timelapse.IS_DIRECTORY):
            if(self.isWritable(self.directory) == Timelapse.IS_WRITABLE):
                if(self.verbose):
                    print("Timelapse directory exists and is writable = " + self.directory)
            else:
                if(self.verbose):
                    print("Timelapse directory is not writable = " + self.directory)
        elif(self.directoryInfo == Timelapse.IS_FILE):
            if(self.verbose):
                print("Timelapse directory is a file = " + self.directory)
        elif(self.directoryInfo == Timelapse.DIRECTORY_DO_NOT_EXIST):            
            os.mkdir(self.directory)
            self.directoryInfo = Timelapse.IS_WRITABLE
            if(self.verbose):
                print("Timelapse directory created = " + self.directory)
        
        # The "output" folder is ok, now we need to start capturing images
        #if(self.directoryInfo == Timelapse.IS_WRITABLE):         
            
    #def __del__(self):

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
    
    def getUrl(self):
        return self.url

    def captureImages(self):
        # Create a folder YYYYMMDD for the day's pictures if no exists
        timestamp = dateUtl.getTimeStamp("%Y%m%d")
        self.directoryInfo = self.isDirectory(self.directory + "/" + timestamp)
        if(self.directoryInfo == Timelapse.DIRECTORY_DO_NOT_EXIST):
            os.mkdir(self.directory + "/" + timestamp)
        # Set the image directory
        self.imageDirectory = self.directory + "/" + timestamp

        # Capture the image
        if(self.url == None or len(self.url) == 0):
            return Timelapse.URL_IS_NOT_SET
        else:
            try:
                urllib.request.urlretrieve(self.url, self.imageDirectory + "/" + dateUtl.getTimeStamp("%Y%m%d%H%M%S") + ".jpg")
            except urllib.error.URLError as e:
                print("<error>URLError=" + str(e))
            except urllib.error.HTTPError as e:
                print("<error>HTTPError=" + str(e))
            except urllib.error.ContentTooShortError as e:
                print("<error>ContentTooShortError=" + str(e))
         

