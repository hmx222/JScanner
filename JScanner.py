import requests
import argparse, urllib3, re,json,os
from urllib.parse import urlparse

urllib3.disable_warnings()

return_List = []


def parse_args():
    """用户输入"""
    parse = argparse.ArgumentParser(description="hi 你好")
    parse.add_argument('-u', '--url', required=True, type=str, help="输入带有http/https的网站URL")
    parse.add_argument('-c', '--cookie', type=str, help="输入cookie，默认为空")
    parse.add_argument('-r', '--header', type=str,
                       default='{"user-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"}',
                       help="输入user-agent,格式为\'{\"cookie\":\"xxxx\",\"user-Agent\":\"xxxx\",\"xxxx\":\"xxxx\"}\'")
    parse.add_argument('-l', '--level', type=int, default=0, help="输入最大递减数，默认为0表示全递减")
    parse.add_argument('-b', '--black-list', help="将黑名单关键词放入black.txt，将会读取它")
    parse.add_argument('-t', '--height', type=int,default=0,help="查找深度")
    parse.add_argument('-w','--wait',type=int,help="网站请求超时等待时间")
    parse.add_argument('-s','--black-status',type=tuple,default=(404,502,500),help="输入您不想要获得的状态码")
    return parse.parse_args()


def urlGet(url, header=None, waitTime=3):
    """请求"""
    if header is not None:
        header = json.loads(header)
    try:
        result = requests.get(url=url, headers=header,verify=False,timeout=waitTime)
    except:
        pass
    else:
        return result


def analysis(content, get_url):
    """数据分析，其中data_list需要从urlGet函数当中获取，get_Url也需要从当中获取"""
    pattern = re.compile(r"(?!.*\.(?:mp3|ogg|wav|avi|mp4|flv|mov|png|jpg|gif|bmp|svg|ico|css))(?:\/\w+)*\/[\w\.]+")
    matches = pattern.findall(content)

    pattern_raw = r"""
              (?:"|')                               # Start newline delimiter
              (
                ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
                [^"'/]{1,}\.                        # Match a domainname (any character + dot)
                [a-zA-Z]{2,}(?!png|css|jpeg|mp4|mp3|gif|ico)[^"']{0,})              # The domainextension and/or path, not ending with png/css/jpeg/mp4/mp3
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
    links = pattern.findall(content)
    relist = [link[0] for link in links if not link[0].endswith(('.css', '.png', '.jpg', '.mp4'))]

    allList = relist + matches
    allList = list(set(allList))
# TODO增加去重

    for mainUrl in allList:
        handled_url = urlparse(get_url)
        httpUrl = handled_url.scheme
        hostUrl = handled_url.netloc
        pathUrl = handled_url.path
        if mainUrl.startswith('/'):
            # 处理以斜杠开头的相对路径
            if mainUrl.startswith('//'):
                temUrl = httpUrl + ':' +mainUrl
                urlObject = urlparse(temUrl)
                if '.' in urlObject.netloc:
                    put_url = httpUrl + ':'+mainUrl
            else: # 此时也就是 / 开头的
                mainUrl = '/' + mainUrl
                temUrl = httpUrl + ':' + mainUrl
                urlObject = urlparse(temUrl)
                if '.' in urlObject.netloc:
                    put_url = httpUrl + ':' +mainUrl
                else:
                    mainUrl = mainUrl[1:]
                    put_url = httpUrl + '://' + hostUrl + mainUrl
        elif mainUrl.startswith('./'):
            # 处理以./开头的相对路径
            put_url = httpUrl + '://' + hostUrl + mainUrl[2:]
        elif mainUrl.startswith('../'):
            # 处理以../开头的相对路径
            put_url = httpUrl + '://' + hostUrl + os.path.normpath(os.path.join(pathUrl, mainUrl))
        elif mainUrl.startswith('http') or mainUrl.startswith('https'):
            # 处理以http或https开头的绝对路径
            put_url = mainUrl
        else:
            # 处理其他情况
            put_url = httpUrl + '://' + mainUrl if not handled_url.netloc else mainUrl
        return_List.append(put_url)

    return list(set(return_List))
def read(filename: str) -> list:
    """文件读取"""
    with open(filename, 'r') as file:
        lines = [line.strip().split(" ")[0] for line in file if line.strip() and line.strip()[0] != "#"]
    return lines

def height(url,header,waitTime,high):
    if type(url) == str:
        url = [url]
        urlFin = []
    for num in range(high):
        for i in url:
            demoResult = urlGet(i,header=header,waitTime=waitTime)
            urlResult = analysis(demoResult.text,i)
            urlFin.extend(urlResult)
        url = []
        url.extend(urlResult)
    return urlFin

def status(url_Object):
    """变更为对状态码的提取"""
    status_code = url_Object.status_code
    return status_code

def decline(url, num):
    if url[:8] == "https://":
        url = url.replace("https://","",1)
        url_list = []
        if num > 1:
            for i in range(num):
                url_list.append("https://"+url)
                url = '/'.join(url.split('/')[:-1])
            url_list.append(url+'/')
            url_list.reverse()
        else:
            parts = url.split('/')
            for i in range(2, len(parts) + 1):
                url_list.append("https://"+'/'.join(parts[:i]))
        return url_list
    else:
        url = url.replace("http://","",1)
        url_list = []
        if num > 1:
            for i in range(num):
                url_list.append("http://"+url)
                url = '/'.join(url.split('/')[:-1])
            url_list.append(url+'/')
            url_list.reverse()
        else:
            parts = url.split('/')
            for i in range(2, len(parts) + 1):
                url_list.append('/'.join(parts[:i]))
        return url_list



if __name__ == "__main__":
    args = parse_args()
    resultObject = urlGet(url=args.url,header=args.header,waitTime=args.wait)
    urlList = analysis(resultObject.text,args.url)
    urlAll = []
    if args.height > 0:
        urlList = urlList + height(urlList,header=args.header,waitTime=args.wait,high=args.heigth)
    for url in urlList:
        urlDemo = decline(url,args.level)
        urlAll.extend(urlDemo)
    urlAll = list(set(urlAll))
    for url in urlAll:
        try:
            result = urlGet(url,header=args.header,waitTime=args.wait)
            code = status(result)
        except:
            print(url , "----------" ,"ERROR")
        else:
            if code in args.black-status:
                pass
            else:
                print(url,"----------",code)






