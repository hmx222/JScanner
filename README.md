### JScanner

#### 此工具能够干什么？

- 能够找到js或者网页源代码当中的路径与url与敏感信息
- 支持黑名单机制

#### 怎么使用？

0、你首先要安装requirements.txt文件当中的依赖性
```shell
pip install -r requirements.txt
```

1、你需要将黑名单的url关键字放入black.txt

2、你需要将url（一个或者多个）放入urls.txt

3、执行（您可以在89行的代码处增加对特定的文件后缀的黑名单只需要  |filetype）

```python
python JScanner.py
python JScanner.py -c cookie 可以指定cookie
```

4、然后你就能在result_urls.txt发现得到的url；在path.txt得到路径信息；在import_info.txt得到敏感信息

5、推荐在你查看信息后，自行去除部分url



原理图：
![1679325040015](https://user-images.githubusercontent.com/60973265/226383307-cc5c8d00-c077-4fd6-ad08-adef1dcc65d1.jpg)

