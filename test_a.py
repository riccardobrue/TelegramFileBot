from urllib.request import urlopen
import urllib
from io import BytesIO

url="https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/505218/IC_Energy_Report_web.pdf"
#url="http://audio.radio24.ilsole24ore.com/radio24_audio/2018/180314-lazanzara.mp3"
object1 = urlopen(url)
object2 =   open('test.zip', 'rb')
#urllib.request.urlretrieve("http://audio.radio24.ilsole24ore.com/radio24_audio/2018/180314-lazanzara.mp3", '/cat.mp3')


object1.name = 'testing.pdf'



#print(object1.read())
print(object1)
print(object2)