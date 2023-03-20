import re
import requests
from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings()


class FileHandle(object):

    def __init__(self):
        self.encode = 'utf-8'

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
        f.write('\n' + content)
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
        rex = '^(?!.*\.(mp4|flv|avi|mp3|wav|jpg|jpeg|gif|png|bmp|css)$)(\.{0,2}/)?[/a-zA-Z0-9_-]+(/[/a-zA-Z0-9_-]+)*$'
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
        for atitle in got_title:
            return atitle

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

    def check_Url(self, outurl: str, geturl: str):
        handled_url = urlparse(geturl)
        http_url = handled_url.scheme
        host_url = handled_url.netloc
        path_url = handled_url.path

        if outurl[:1] == '/':
            if geturl[:2] == '//':
                put_url = http_url + ':' + outurl
                return put_url
            else:
                put_url = host_url + '://' + host_url + outurl
                return put_url

        elif outurl[:2] == './':
            put_url = http_url + '://' + host_url + outurl
            return put_url

        elif outurl[:3] == '../':
            put_url = http_url + '://' + host_url + path_url + '../' + outurl
            return put_url

        elif outurl[:4] == 'http' or outurl[:4] == 'https':
            put_url = outurl
            return put_url

        else:
            put_url = http_url + '://' + host_url + path_url + '/' + outurl
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
        for afound_email_info in found_email_info:
            file.write(content=afound_email_info, type='a', filename='import_Info.txt')
        for afound_phone_info in found_phone_info:
            file.write(content=afound_phone_info, type='a', filename='import_Info.txt')

        found_info = []
        found_info.extend(found_email_info)
        found_info.extend(found_phone_info)

        found_path = []
        found_path.extend(path.SearchPath(sourceCode))
        for apath in found_path:
            file.write(content=apath, type='w', filename='path.txt')

        found_url = url.extract_URL(sourceCode)
        blacklist = file.Read(filename='black.txt')

        userop = input("是否需要将404与500添加到url.txt当中？")
        while True:
            for efound_url in found_url:
                for eblack in blacklist:
                    if eblack in efound_url:
                        efound_url = None
                if efound_url is None:
                    continue

                checked_url = url.check_Url(efound_url, eurl)
                # out url
                try:
                    status_coded = url.status_code(checked_url)
                    got_title = url.title(checked_url)
                except:
                    continue
                else:
                    if userop == 'y':
                        file.write(content=checked_url, type="a", filename="urls.txt")
                        file.write(content=checked_url + '-----' + str(status_coded), type='a',
                                   filename='result_urls.txt')
                    else:
                        if status_coded > 500 or status_coded == 404:
                            continue
                        else:
                            file.write(content=checked_url, type="a", filename="urls.txt")
                            if url.title(checked_url) is None:
                                continue
                            file.write(content=checked_url + '-----' + str(status_coded) + '-----' + url.title(checked_url), type='a',
                                       filename='result_urls.txt')

            option = input("已经将爬取到的url放入url.txt与result_url.txt,是否要继续爬取？（您可以自己修改）")
            if option == 'y':
                file.write(content='', type='w', filename='urls.txt')
                file.write(content='', type='w', filename='path.txt')
                found_url.extend(file.Read(filename='urls.txt'))
            else:
                break
