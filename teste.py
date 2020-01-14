import urllib.request as urllib
import numpy as np
from PIL import Image

#urllib.request.urlretrieve("http://localhost:8080/live_image", "aaaaa.jpg")


resp = urllib.urlopen("http://localhost:8080/live_image", timeout=1)
image = np.asarray(bytearray(resp.read()), dtype="uint8")
Image.fromarray(image).convert("RGB").save("art.jpg") # don't need to convert
