import os

class Timelapse:

    IS_WRITABLE = 1

    DIRECTORY_DO_NOT_EXIST = -1
    IS_DIRECTORY = -2
    IS_FILE = -3
    IS_NOT_WRITABLE = -4

    def __init__(self, directory, verbose=False):
        self.directory = directory
        self.verbose = verbose
        dirInfo = IsDirectory(self.directory)
        if(dirInfo == Timelapse.IS_DIRECTORY):
            if(IsWritable(self.directory) == Timelapse.IS_WRITABLE):
                if(self.verbose):
                    print("Timelapse directory is writable = " + self.directory)
        elif(dirInfo == Timelapse.IS_FILE):
                if(self.verbose):
                    print("Timelapse directory is a file = " + self.directory)
        elif(dirInfo == Timelapse.DIRECTORY_DO_NOT_EXIST):            
            os.mkdir(self.directory)
            if(self.verbose):
                    print("Timelapse directory created = " + self.directory)

    #def __del__(self):

    def IsDirectory(directory):
        if os.path.exists(path):
            if os.path.isfile(fnm):
                return Timelapse.IS_FILE
            else:
                return Timelapse.IS_DIRECTORY
        else:
            return Timelapse.DIRECTORY_DO_NOT_EXIST

    def IsWritable(directory):
        if(os.access(directory, os.X_OK | ox.W_OK) == True):
            return Timelapse.IS_WRITABLE
        else:
            return Timelapse.IS_NOT_WRITABLE
