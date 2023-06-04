from urllib.parse import urlparse

url = "http://jw.ecut.edu.cn"
url1 = "http://122/234.html"
#url = url.replace('/','')
demo = urlparse(url1)
print(demo.netloc)
print(demo.path)