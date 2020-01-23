import urllib.request
import numpy as np
from PIL import Image

try:
    urllib.request.urlretrieve("http://raspiwebcam.local:8081/?action=snapshot", "aaaaa.jpg")
except urllib.error.URLError as e:
    print("<error>URLError=" + str(e))
except urllib.error.HTTPError as e:
    print("<error>HTTPError=" + str(e))
except urllib.error.ContentTooShortError as e:
    print("<error>ContentTooShortError=" + str(e))



# resp = urllib.urlopen("http://raspiwebcam.local:8081/?action=snapshot", timeout=1)
# image = np.asarray(bytearray(resp.read()), dtype="uint8")
# Image.fromarray(image).convert("RGB").save("art.jpg") # don't need to convert
