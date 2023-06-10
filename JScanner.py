import requests
import argparse, urllib3, re, ast, os, time, random
from urllib.parse import urlparse
import xlsxwriter as xw
from bs4 import BeautifulSoup

urllib3.disable_warnings()

return_url_list = []
excelList = []


def parse_args():
    """用户输入"""
    parse = argparse.ArgumentParser(description="hi 你好")
    parse.add_argument('-u', '--url', required=True, type=str, help="输入带有http/https的网站URL")
    parse.add_argument('-r', '--header', type=ast.literal_eval,
                       default="{'user-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}",
                       help="输入user-agent,格式为\"{\'cookie\':\'xxxx\',\'user-Agent\':\'xxxx\',\'xxxx\':\'xxxx\'}\"")
    parse.add_argument('-l', '--level', type=int, default=0, help="输入最大递减数，默认为0表示全递减")
    parse.add_argument('-H', '--height', type=int, default=0, help="查找深度")
    parse.add_argument('-w', '--wait', type=int, default=3, help="网站请求超时等待时间")
    parse.add_argument('-a', '--appoint', type=str, help="读取指定文件")
    parse.add_argument('-T', '--time', type=int, default=0, help="请求间隔延时")
    parse.add_argument('-B', '--blackStatus', type=ast.literal_eval, default=(404, 502, 500),
                       help="输入您不想要获得的状态码,格式：-s \"(xxx,xxx)\"")
    parse.add_argument('-o', '--out', type=str, help="输出为Excel表格")
    return parse.parse_args()


def url_request(url, header, wait_time=3):
    """请求"""
    try:
        request_url_object = requests.get(url=url, headers=header, verify=False, timeout=wait_time)
    except:
        pass
    else:
        return request_url_object


def analysis(source, url):
    """数据分析，其中data_list需要从urlGet函数当中获取，get_Url也需要从当中获取"""
    pattern = re.compile(r"(?!.*\.(?:mp3|ogg|wav|avi|mp4|flv|mov|png|jpg|gif|bmp|svg|ico|css))(?:\/\w+)*\/[\w\.]+")
    matches = pattern.findall(source)

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
    links = pattern.findall(source)
    relist = [link[0] for link in links if not link[0].endswith(('.css', '.png', '.jpg', '.mp4'))]

    all_list = relist + matches
    all_list = list(set(all_list))  # 此时汇聚的是二者的信息，进行了第一次去重
    for main_url in all_list:
        handled_url = urlparse(url)
        Protocol = handled_url.scheme  # http、https协议
        Domain = handled_url.netloc  # 域名
        Path = handled_url.path  # 路径
        if main_url.startswith('/'):
            # 处理以斜杠开头的相对路径
            if main_url.startswith('//'):
                temp_url = Protocol + ':' + main_url
                try:
                    parse_return_object = urlparse(temp_url)
                except:
                    continue
                else:
                    if '.' in parse_return_object.netloc:
                        return_url = Protocol + ':' + main_url
            else:  # 此时也就是 / 开头的
                main_url = '/' + main_url
                temp_url = Protocol + ':' + main_url
                try:
                    parse_return_object = urlparse(temp_url)
                except:
                    continue
                else:
                    if '.' in parse_return_object.netloc:
                        return_url = Protocol + ':' + main_url
                    else:
                        main_url = main_url[1:]
                        return_url = Protocol + '://' + Domain + main_url
        elif main_url.startswith('./'):
            # 处理以./开头的相对路径
            return_url = Protocol + '://' + Domain + main_url[2:]
        elif main_url.startswith('../'):
            # 处理以../开头的相对路径
            return_url = Protocol + '://' + Domain + os.path.normpath(os.path.join(Path, main_url))
        elif main_url.startswith('http') or main_url.startswith('https'):
            # 处理以http或https开头的绝对路径
            return_url = main_url
        else:
            # 处理其他情况
            return_url = Protocol + '://' + main_url if not handled_url.netloc else main_url
        return_url_list.append(return_url)

    return return_url_list


def read(filename: str) -> list:
    """文件读取"""
    with open(filename, 'r') as file:
        lines = [line.strip().split(" ")[0] for line in file if line.strip() and line.strip()[0] != "#"]
    return lines


def status(Object):
    """变更为对状态码的提取"""
    try:
        status_code = Object.status_code
    except:
        return "NULL"
    else:
        return status_code


def returnLength(Object):
    """返回值长度"""
    try:
        return_length = Object.text
    except:
        return "NULL"
    else:
        return len(return_length)


def heightScan(url, header, wait_time, high):
    return_murl_list = []
    for num in range(high):
        for i in url:
            Object = url_request(i, header=header, wait_time=wait_time)
            if status(Object) == 200:
                urlResult = analysis(Object.text, i)
                return_murl_list.extend(urlResult)
        url = []
        url.extend(return_murl_list)
    return return_murl_list


def decline(url, num):
    if url[:8] == "https://":
        url = url.replace("https://", "", 1)
        url_list = []
        if num > 1:
            for i in range(num):
                url_list.append("https://" + url)
                url = '/'.join(url.split('/')[:-1])
            url_list.append(url + '/')
            url_list.reverse()
        else:
            parts = url.split('/')
            for i in range(2, len(parts) + 1):
                url_list.append("https://" + '/'.join(parts[:i]))
        return url_list
    else:
        url = url.replace("http://", "", 1)
        url_list = []
        if num > 1:
            for i in range(num):
                url_list.append("http://" + url)
                url = '/'.join(url.split('/')[:-1])
            url_list.append(url + '/')
            url_list.reverse()
        else:
            parts = url.split('/')
            for i in range(2, len(parts) + 1):
                url_list.append("http://" + '/'.join(parts[:i]))
        return url_list


def get_title(Object):
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(Object.content, 'html.parser')
    # 获取网页标题
    try:
        title = soup.title.string
    # 返回网页标题
    except:
        return "NULL"
    else:
        return title


def writeExcel(dataList):
    # 生成文件名（当前时间戳 + 随机数）
    fileName = int(time.mktime(time.localtime())) + random.randint(1000, 9999)
    # 创建工作簿
    workbook = xw.Workbook(str(fileName) + ".xlsx")
    # 创建子表
    worksheet1 = workbook.add_worksheet("sheet1")
    # 激活表
    worksheet1.activate()
    # 设置表头
    sheet_header = ['URL', '状态码', '长度', '标题']
    # 从A1单元格开始写入表头
    worksheet1.write_row('A1', sheet_header)
    # 设置第一列的宽度为 50
    worksheet1.set_column(0, 0, 50)
    # 遍历数据列表
    for i in range(len(dataList)):
        # 获取当前数据的 URL、状态码、内容长度和标题
        try:
            writeUrl, statusCode, contentLength, url_title = dataList[i]
        except ValueError:  # 假如不足四个元素就直接忽略
            pass
        else:  # 在表格中写入 URL、状态码、内容长度和标题
            worksheet1.write(i + 1, 0, writeUrl)
            worksheet1.write(i + 1, 1, statusCode)
            worksheet1.write(i + 1, 2, contentLength)
            worksheet1.write(i + 1, 3, url_title)
    # 关闭工作簿
    workbook.close()


if __name__ == "__main__":
    args = parse_args()
    Object = url_request(url=args.url, header=args.header, wait_time=args.wait)
    first_url_list = analysis(Object.text, args.url)  # 此时会获取得到第一次探测url得到的信息
    all_url_list = []
    if args.height > 0:  # 假如设置了深度查找就步入
        urlList2 = heightScan(first_url_list, header=args.header, wait_time=args.wait, high=args.height)
        first_url_list = list(set(first_url_list + urlList2))  # 第二次去重，主要是为了为下面的代码减轻工作量
    for url in first_url_list:
        urlDemo = decline(url, args.level)
        all_url_list.extend(urlDemo)
    all_url_list = list(set(all_url_list))  # 此时会进行第三次去重，去重的是总url，主要是去除部分可能一级目录相同的问题
    for url in all_url_list:
        try:
            time.sleep(args.time)  # 时间间隔
            result = url_request(url, header=args.header, wait_time=args.wait)
            code = status(result)  # 状态码
            outLength = returnLength(result)  # 返回长度
            title = get_title(result)  # 获得标题
        except:
            if args.out:
                excelList.append((url, "ERROR"))
            else:
                print(url, "----------", "ERROR")
        else:
            if code in args.blackStatus:
                pass
            else:
                if args.out:
                    excelList.append((url, code, outLength, title))  # 将所有的数据进行存储，然后写入Excel
                else:
                    print(url, "----------", code, "---------", outLength, "----------", title)
    if args.out:
        writeExcel(excelList)
