import os
import sys
import threading
import requests

sys.path.append('../pythonUtils')
import TDateUtil as dateUtl

class Timelapse:

    IS_WRITABLE = 1
    STATUS_OK = 0
    DIRECTORY_DO_NOT_EXIST = -1
    IS_DIRECTORY = -2
    IS_FILE = -3
    IS_NOT_WRITABLE = -4

    def __init__(self, directory, verbose=False):
        print(dateUtl.getDateTime())
        self.directory = directory
        self.verbose = verbose

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

    # def captureImages(self):
    #     #create a folder YYYYMMDD for the day's pictures if no exists
    #     timestamp = dateUtl.getTimeStamp("%Y%m%d")
    #     self.directoryInfo = self.isDirectory(self.directory + "/" + timestamp)
    #     if(self.directoryInfo == Timelapse.DIRECTORY_DO_NOT_EXIST)
    #         os.mkdir(self.directory + "/" + timestamp)
    #     #else:

