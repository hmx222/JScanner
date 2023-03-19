import re
import requests
from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings()


class FileHandle(object):

    def __init__(self):
        self.encode = 'gbk'

    def Read(self, filename):
        lines = []
        file = open(filename, 'r', encoding=self.encode)
        while True:
            text = file.readline().strip()
            if not text:
                break
            if text[0] == "#":
                continue
            text = text.split(" ")[0]
            lines.append(text)
        file.close()
        return lines

    def write(self, content: str, type: str, filename):
        f = open(filename, type, encoding=self.encode)
        f.write(content + "\n")
        f.close()


class post_extra(FileHandle):

    def SearchPhone(self, content):
        phone = "^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$"  # 对于电话号码的查找
        response = re.findall(phone, content)
        return response

    def SearchEmail(self, content):
        email = '^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'  # 对于邮箱的查找
        response = re.findall(email, content)
        return response

    def SearchPath(self, content):
        rex = '[\'"](\/[^<>/\\\|:""\\ *\?]+){2,}[\'"]'
        response = re.findall(rex, content)
        return response

    def tileScan(self, content):
        response = re.findall("<title>(.*?)</title>", content)
        return response


class urlHandle(post_extra):
    def status_code(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
                   'referer': 'https://www.baidu.com', "Connection": "close"}
        response = requests.get(url=url, headers=headers, timeout=8, verify=False).status_code  # 对于输入网站的请求
        return response

    def source_code(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
                   'referer': 'https://www.baidu.com', "Connection": "close"}
        response = requests.get(url=url, headers=headers, timeout=8, verify=False).text  # 对于输入网站的请求
        return response

    def title(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
                   'referer': 'https://www.baidu.com', "Connection": "close"}
        response = requests.get(url=url, headers=headers, timeout=8, verify=False).text  # 对于输入网站的请求
        got_title = super().tileScan(response)
        return got_title

    def extract_URL(self, JS):
        pattern_raw = r"""
    	  (?:"|')                               # Start newline delimiter
    	  (
    	    ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
    	    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
    	    [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
    	    |
    	    ((?:/|\.\./|\./)                    # Start with /,../,./
    	    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
    	    [^"'><,;|()]{1,})                   # Rest of the characters can't be
    	    |
    	    ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
    	    [a-zA-Z0-9_\-/]{1,}                 # Resource name
    	    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
    	    (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
    	    |
    	    ([a-zA-Z0-9_\-]{1,}                 # filename
    	    \.(?:php|asp|aspx|jsp|json|
    	         action|html|js|txt|xml)             # . + extension
    	    (?:\?[^"|']{0,}|))                  # ? mark with parameters
    	  )
    	  (?:"|')                               # End newline delimiter
    	"""
        pattern = re.compile(pattern_raw, re.VERBOSE)
        result = re.finditer(pattern, str(JS))
        if result == None:
            return None
        js_url = []
        return [match.group().strip('"').strip("'") for match in result
                if match.group() not in js_url]

    def check_Url(self, outurl:str,geturl:str):
        handled_url = urlparse(geturl)
        http_url = handled_url.scheme
        host_url = handled_url.netloc
        path_url = handled_url.path

        if geturl[:1] == '/':
            if geturl[:2] == '//':
                put_url = http_url + ':' + outurl
                return put_url
            else:
                put_url = host_url + '://' + host_url + outurl
                return put_url

        elif geturl[:2] == './':
            put_url = http_url + '://' + host_url + outurl
            return put_url

        elif geturl[:3] == '../':
            put_url = http_url + '://' + host_url + path_url + '../' + outurl
            return put_url

        else:
            put_url = http_url + '://' + host_url + path_url + outurl
            return put_url



class otherFunction(post_extra):
    def list_con(self, listTemp, n):
        for i in range(0, len(listTemp), n):
            yield listTemp[i:i + n]


if __name__ == "__main__":
    file = FileHandle()
    url = urlHandle()
    importInfo = post_extra()
    path = post_extra()

    get_list = file.Read('black.txt')
    get_url = file.Read('urls.txt')
    for eurl in get_url:
        sourceCode = url.source_code(eurl)

        found_phone_info = importInfo.SearchPhone(sourceCode)
        found_email_info = importInfo.SearchEmail(sourceCode)

        found_info = []
        found_info.extend(found_email_info)
        found_info.extend(found_phone_info)

        found_path = []
        found_path.extend(path.SearchPath(sourceCode))

        found_url = url.extract_URL(sourceCode)
        for blackurl in file.Read(filename='black.txt'):
            if blackurl in found_url:
                found_url = None

        option = input("已经将下次要检索的url放入url.txt,您可以自定义来删除部分，是否需要继续？")

        for efound_url in found_url:
            checked_url = url.check_Url(efound_url, eurl)
            # out url
            try:
                status_coded = url.status_code(checked_url)
                got_title = url.title(checked_url)
            except:
                continue
            else:
                file.write(content=checked_url + '-----' + str(status_coded), type='a', filename='result_urls.txt')
                if option == "y":
                    file.write(content=checked_url, type="w", filename="urls.txt")
                else:
                    break
