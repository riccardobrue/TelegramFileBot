from urllib.request import urlopen
import urllib
import requests
from io import BytesIO

url="https://github.com/riccardobrue/hello_world/blob/master/testing_zip.zip?raw=true"
object1 = urlopen(url)
#urllib.request.urlretrieve("http://audio.radio24.ilsole24ore.com/radio24_audio/2018/180314-lazanzara.mp3", '/cat.mp3')


file_name, headers = urllib.request.urlretrieve(url)
ff=open(file_name, 'rb')
files = {'file': ('report.xls', ff)}

url2 = 'http://riccardobruetesting.altervista.org/APIs/file/file_api.php'
r = requests.post(url2, files=files)
print("TEXT: "+r.text)





object1.name = 'testing.zip'
meta = object1.info()
#print (int(meta["Content-Length"]))

file=open('test.py', 'rb')
print(ff)



print(file_name)
print(object1)