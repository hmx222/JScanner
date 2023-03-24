# encoding=utf8
import re
from urllib.parse import urlparse
import requests

requests.packages.urllib3.disable_warnings()


class FileHandle:
    def __init__(self):
        self.encode = 'utf-8'

    def read(self, filename: str) -> list:
        with open(filename, 'r', encoding=self.encode) as file:
            lines = [line.strip().split(" ")[0] for line in file if line.strip() and line.strip()[0] != "#"]
        return lines

    def write(self, content: str, mode: str, filename: str) -> bool:
        with open(filename, mode, encoding=self.encode) as f:
            f.write('\n' + content)
            return True

    from typing import List

    def deduplication_file(self, input_file: str, output_file: str) -> None:
        text_set = set()
        with open(input_file, 'r', encoding='utf-8') as input_f:
            for line in input_f:
                # 去掉文本数据中的空格和换行符
                line = line.strip()

                # 将非空的文本数据添加到set集合中
                if line:
                    text_set.add(line)

        # 将去重后的文本数据写入输出文件中
        with open(output_file, 'w', encoding='utf-8') as output_f:
            for text in text_set:
                output_f.write(text + '\n')


class post_extra(FileHandle):
    phone_regex = r'(?:\d{1,3}\.){3}\d{1,3}|[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*\.[a-zA-Z]{2,4}|[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[012])(?:0[1-9]|[12]\d|3[01])[\dxX]|1[3-9]\d{9}|password'

    title_regex = r'<title>(.*?)</title>'

    def extract_js_paths(self,js_code):
        pattern = re.compile(r"'(?!.*\.(?:mp3|ogg|wav|avi|mp4|flv|mov|png|jpg|gif|bmp|svg|ico|css))(?:\/\w+)*\/\w+\/'")

        matches = pattern.findall(js_code)
        return matches
    def Searchinfo(self, content):
        response = re.findall(self.phone_regex, content)
        return response

    def tileScan(self, content):
        response = re.findall(self.title_regex, content)
        return response


class urlHandle(post_extra):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
               'referer': 'https://www.baidu.com', "Connection": "close"}
    timeout = 8
    verify = False

    def get_request(self, url):
        response = requests.get(url=url, headers=self.headers, timeout=self.timeout, verify=self.verify)
        return response

    def status_code(self, url):
        response = self.get_request(url)
        return response.status_code

    def source_code(self, url):
        response = self.get_request(url)
        return response.text

    def title(self, url):
        response = self.get_request(url)
        got_title = super().tileScan(response.text)
        return got_title[0] if got_title else None

    def extract_links(self, html):
        pattern_raw = r"""
              (?:"|')                               # Start newline delimiter
              (
                ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
                [^"'/]{1,}\.                        # Match a domainname (any character + dot)
                [a-zA-Z]{2,}(?!png|css|jpeg|mp4|mp3)[^"']{0,})              # The domainextension and/or path, not ending with png/css/jpeg/mp4/mp3
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
        links = pattern.findall(html)
        return [link[0] for link in links if not link[0].endswith(('.css', '.png', '.jpg', '.mp4'))]

    def check_url(self, out_url: str, get_url: str):
        handled_url = urlparse(get_url)
        http_url = handled_url.scheme
        host_url = handled_url.netloc
        path_url = handled_url.path
        prefix_map = {
            '/': lambda: http_url + ':' + out_url if get_url.startswith(
                '//') else host_url + '://' + host_url + out_url,
            './': lambda: http_url + '://' + host_url + out_url,
            '../': lambda: http_url + '://' + host_url + path_url + '/../' + out_url,
            'http': lambda: out_url,
            'https': lambda: out_url,
            'default': lambda: http_url + '://' + host_url + path_url + '/' + out_url
        }
        prefix = next((p for p in prefix_map.keys() if out_url.startswith(p)), 'default')
        put_url = prefix_map[prefix]()
        return put_url


if __name__ == "__main__":
    file = FileHandle()
    url = urlHandle()
    importInfo = post_extra()
    path = post_extra()

    get_list = file.read('black.txt')
    get_url = file.read('urls.txt')
    for eurl in get_url:
        sourceCode = url.source_code(eurl)
        found_infos = importInfo.Searchinfo(sourceCode)

        for afound_phone_info in found_infos:
            file.write(content=afound_phone_info, mode='a', filename='import_Info.txt')

        found_path = []
        found_path.extend(path.extract_js_paths(sourceCode))
        for apath in found_path:
            file.write(content=apath, mode='w', filename='path.txt')

        found_url = url.extract_links(sourceCode)
        found_url.append("end")
        blacklist = file.read(filename='black.txt')

        userop = input("是否需要将404与500添加到url.txt当中？")
        while True:
            for efound_url in found_url:
                for eblack in blacklist:
                    if eblack in efound_url:
                        efound_url = None
                if efound_url == "end":
                    break
                if efound_url is None:
                    continue

                checked_url = url.check_url(efound_url, eurl)
                # out url
                try:
                    status_coded = url.status_code(checked_url)
                    got_title = url.title(checked_url)
                except:
                    continue
                else:
                    if userop == 'y':
                        file.write(content=checked_url, mode="a", filename="urls.txt")
                        file.write(content=checked_url + '-----' + str(status_coded), mode='a',
                                   filename='result_urls.txt')
                    else:
                        if status_coded > 500 or status_coded == 404:
                            continue
                        else:
                            file.write(content=checked_url, mode="a", filename="urls.txt")
                            if url.title(checked_url) is None:
                                continue
                            file.write(
                                content=checked_url + '-----' + str(status_coded) + '-----' + url.title(checked_url),
                                mode='a',
                                filename='result_urls.txt')

            file.deduplication_file(input_file='urls.txt', output_file='urls.txt')
            file.deduplication_file(input_file='result_urls.txt', output_file='result_urls.txt')
            option = input("已经将爬取到的url放入url.txt与result_url.txt,是否要继续爬取？（您可以自己修改）")
            if option == 'y':
                file.write(content='', mode='w', filename='urls.txt')
                file.write(content='', mode='w', filename='path.txt')
                found_url.extend(file.read(filename='urls.txt'))
            else:
                break
