import logging
import configparser # for .ini file
import os
import sys
import subprocess # unix commands with arguments
import shutil # remove directory tree
import glob # wildcards
import threading
import schedule #REF: https://pypi.org/project/schedule/
import urllib.request
import subprocess
sys.path.append('../pythonUtils')
import TDateUtil as dateUtl
from twython import Twython

class Timelapse:   

    # TIMELAPSE constants
    TIME_TO_TIMELAPSE = "01:00:00"
    INTERVAL_TO_CAPTURE_IMG = 120   # time in seconds
    CAPTURE_IMG_RETRIES = 3
    FFMPEG_PROCESS_TIMEOUT = 600    # time in seconds

    # TWITTER constants
    TWITTER_ENABLED = False
    TWITTER_CONSUMER_KEY = ""
    TWITTER_CONSUMER_SECRET = ""
    TWITTER_ACCESS_TOKEN = ""
    TWITTER_ACCESS_TOKEN_SECRET = ""

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
        # Config constants by ini file
        self.config = configparser.ConfigParser()
        if(os.path.exists("timelapse.ini") == False):
            logger.warning("timelapse.ini not found, using default values")
        else:
            self.config.read("timelapse.ini")
            Timelapse.TIME_TO_TIMELAPSE = str(self.config["TIMELAPSE"]["time_to_timelapse"])
            Timelapse.INTERVAL_TO_CAPTURE_IMG = int(self.config["TIMELAPSE"]["interval_to_capture_img"])
            Timelapse.CAPTURE_IMG_RETRIES = int(self.config["TIMELAPSE"]["capture_img_retries"])
            Timelapse.FFMPEG_PROCESS_TIMEOUT = int(self.config["TIMELAPSE"]["ffmpeg_process_timeout"])
            Timelapse.TWITTER_ENABLED = self.config["TWITTER"].getboolean("enabled")
            if(Timelapse.TWITTER_ENABLED == True):
                Timelapse.TWITTER_CONSUMER_KEY = str(self.config["TWITTER"]["consumer_key"])
                Timelapse.TWITTER_CONSUMER_SECRET = str(self.config["TWITTER"]["consumer_secret"])
                Timelapse.TWITTER_ACCESS_TOKEN = str(self.config["TWITTER"]["access_token"])
                Timelapse.TWITTER_ACCESS_TOKEN_SECRET = str(self.config["TWITTER"]["access_token_secret"])
            else:
                self.logger.debug("TWITTER_ENABLED=" + str(Timelapse.TWITTER_ENABLED))

        self.logger.debug("Init, directory=" + directory + ", url=" + url)        
        self.directory = directory     
        self.url = url
        self.schedule=schedule
        # Set timer to capture the images
        self.timer = threading.Timer(Timelapse.INTERVAL_TO_CAPTURE_IMG, self.captureImage) 
        # Set hour for transform images into timelapse and upload
        self.schedule.every().day.at(Timelapse.TIME_TO_TIMELAPSE).do(self.doTimelapse)
        # to query ffmpegProcess on doTimelapse
        self.ffmpegProcessStarted=False
        self.ffmpegProcess=0

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
        schedule.clear()
    
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

    def doTimelapse(self):        
        # Remove if already have a temporary folder output/timelapse_*
        fileList = glob.glob(self.directory + "/timelapse_*")
        for filePath in fileList:
            shutil.rmtree(filePath)

        # Copy the last folder to a temporary location: output/timelapse_{YESTERDAY_TIMESTAMP}
        subprocess.call(["cp", "-r", "output/" + dateUtl.getYesterdayTimeStamp(), "output/timelapse_" + dateUtl.getYesterdayTimeStamp()])

        # Rename all files to a sequence img_{0000-9999}.jpg
        i=0
        for filename in os.listdir("output/timelapse_" + dateUtl.getYesterdayTimeStamp()):
            src=self.directory+"/timelapse_" + dateUtl.getYesterdayTimeStamp() + "/" + filename
            dst=self.directory+"/timelapse_{}/img_{:04d}.jpg".format(dateUtl.getYesterdayTimeStamp(), i)   
            os.rename(src, dst)  
            i+=1
        self.logger.debug("Renamed %s files in %s", str(i), self.directory+"/timelapse_" + dateUtl.getYesterdayTimeStamp())

        # Do timelapse with ffmpeg. These configs are specials to fit the video requirement for twitter
        # ffmpeg -f image2 -framerate 30 -i img_%04d.jpg -vcodec libx264 -pix_fmt yuv420p -strict -2 -acodec aac -q:v 1 test.mp4
        #   -f image2, tells ffmpeg that is coming a sequence of image for input
        #   -framerate 30, video with 30 images/second, so 1s of video = 1h of the day
        #   -i img_%04d.jpg, the image sequence pattern
        #   -vcodec libx264, codec mp4
        #   -pix_fmt yuv420p, pixel format
        #   -strict -2
        #   -acodec aac, audio codec, enve video has no sound
        #   -q:v 1, video quality, where 1 is higher and 31 is the lower
        #   -test.avi, output file
        self.ffmpegProcess = subprocess.Popen([ "ffmpeg", "-f", "image2", 
                                                "-framerate", "30", 
                                                "-i", self.directory+"/timelapse_"+dateUtl.getYesterdayTimeStamp()+"/img_%04d.jpg", 
                                                "-vcodec", "libx264",
                                                "-pix_fmt", "yuv420p",
                                                "-strict", "-2",
                                                "-acodec", "aac",
                                                "-q:v", "1",
                                                self.directory+"/timelapse_"+dateUtl.getYesterdayTimeStamp()+"/"+dateUtl.getYesterdayTimeStamp()+".mp4"]
                                                ,shell=False
                                                ,stderr=subprocess.DEVNULL # for no stdout on console
                                                ,stdout=subprocess.DEVNULL)
                                                #timeout=Timelapse.FFMPEG_PROCESS_TIMEOUT)
        self.logger.debug("ffmpegProcess started")
        
        # Need to free the program, to keep capturing images
        # So we need to know if ffmpegProcess is over to manipulate the generated video
        # Lets do it every 30s
        self.schedule.every(30).seconds.do(self.ffmpegCheckProcess).tag("ffmpegProcess")

    def ffmpegCheckProcess(self):
        poll = self.ffmpegProcess.poll()
        if poll == None:
            self.logger.debug("ffmpegProcess is alive")
        else:
            self.logger.debug("ret ffmpegProcess=%s", str(poll))
            self.schedule.clear("ffmpegProcess")
            if(poll == 0):
                videoPath=self.directory+"/timelapse_"+dateUtl.getYesterdayTimeStamp()+"/"+dateUtl.getYesterdayTimeStamp()+".mp4"
                if(Timelapse.TWITTER_ENABLED == True):                
                    self.logger.debug("ffmpeg process ended, uploading it to twitter, videoPath=%s", videoPath)                
                    self.uploadVideoTwitter(videoPath)
                else:
                    self.logger.debug("ffmpeg process ended")

    def runPendingSchedules(self):
        self.schedule.run_pending()
    
    def uploadVideoTwitter(self, videoPath):
        logging.getLogger("twython").setLevel(logging.ERROR)                        
        logging.getLogger("requests_oauthlib").setLevel(logging.ERROR)
        logging.getLogger("oauthlib").setLevel(logging.ERROR)

        # authentication of consumer key and secret 
        twitter = Twython(Timelapse.TWITTER_CONSUMER_KEY, Timelapse.TWITTER_CONSUMER_SECRET,
                          Timelapse.TWITTER_ACCESS_TOKEN, Timelapse.TWITTER_ACCESS_TOKEN_SECRET)      
        
        video = open(videoPath, 'rb')
        response = twitter.upload_video(media=video, media_type='video/mp4')
        twitter.update_status(status="A beauty timelapse from Araras, Sao Paulo, Brazil. It's from " + dateUtl.getYesterdayTimeStamp("%d/%m/%Y") + "."
                              ,media_ids=[response['media_id']])