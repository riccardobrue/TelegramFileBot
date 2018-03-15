from urllib.request import urlopen
import urllib
from io import BytesIO

url="https://github.com/riccardobrue/hello_world/blob/master/testing_zip.zip?raw=true"
object1 = urlopen(url)
#urllib.request.urlretrieve("http://audio.radio24.ilsole24ore.com/radio24_audio/2018/180314-lazanzara.mp3", '/cat.mp3')


object1.name = 'testing.zip'
meta = object1.info()
print (int(meta["Content-Length"]))


#print(object1.read())
print(object1)