from importlib.metadata import files
import requests

URL = 'http://127.0.0.1:5000/map'

file = {'file': open('test.SLAM', 'rb')}
req1 = requests.post(URL, files=file, data= {"id":1})
req2 = requests.get(URL)
with open("response.SLAM", "wb") as f:
    f.write(req2.content)
req2.content

