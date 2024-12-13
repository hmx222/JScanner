### JScanner

#### 为什么要写这款工具？

在2022年，我测试了无数网站，但是某些网站无论如何都不能搞定它，看了好多别人的实战思路，我总结出来了一点，那些大佬们总是会在前期在js文件当中收集信息，收集到别人在fofa还是鹰图上面探测不到了信息。于是我便想写一款工具来帮助自己在前期更好的探测。

部分正则表达式来自于：https://github.com/GerbenJavado/LinkFinder

#### 这款这款工具能够干什么？

- 探测网页源代码，发现js文件
- 探测js文件，发现路径
- 支持自定义状态码
- 支持多URL请求
- 支持目录的递减访问操作（更好的打出目录遍历漏洞）
- 支持深度查找
- 支持对标题与返回值长度的输出
- 支持多URL的查找
- 配合findsomething筛选出有效路径

##### 推荐用法（在不配合findsomething插件下）
```shell
python JScanner.py -u "http://example.com" -o excel -T 0.1 
```
##### 推荐用法（配合findsomething插件下）
path.txt内容应该为findsomething得来的路径
```shell
python JScanner.py -u "http://example.com" -o excel -T 0.1 -f path.txt
```

#### 这款工具怎么使用？

```shell
python JScanner.py -h
```

你可以看到具体的帮助文档

##### 默认情况下：

```shell
python JScanner.py -u "https://example.com/xxxxx"
```

##### 设置请求间隔延时

```shell
python Jscanner.py -u "https://example.com/xxxxx" -T 2
```

##### 设置header请求头

```shell
python Jscanner.py -u "https://example.com/xxxxx" -r "{'cookie':'xxxx','user-Agent':'xxxx','xxxx':'xxxx'}"
```

##### 设置查找深度

```shell
python Jscanner.py -u "https://example.com/xxxxx" -H 2
```

建议：设置的查找深度不要超过2，或者有时候可以不进行设置

##### 设置最大递减

```shell
python Jscanner.py -u "https://example.com/xxxxx" -l 1
```

在默认情况下为0，表示全递减；举个栗子：

```
假如你设置了1，则会将https://example.com/xxx/xxx/xxx，拆分为https://example.com/xxx/xxx，https://example.com/xxx/xxx/xxx；假如设置了0，则会全部进行拆分：https://example.com/xxx/xxx/xxx，https://example.com/xxx/xxx/，https://example.com/xxx/，https://example.com/
```

##### 设置您不想要的状态码

```shell
python Jscanner.py -u "https://example.com/xxxxx" -B "(404,502)"
```
##### 输出为Excel表格的形式（推荐）
```shell
python Jscanner.py -u "https://example.com/xxxxx" -o excel
```
##### 配合findsomething插件来完成信息收集
将findsomething当中的路径复制到文本文件当中，使用下面的命令
下面的命令不仅会使用当前的脚步内置的正则表达式来进行匹配，还会使用path.txt文件当中的路径进行拼接，最后去重输出。

```shell
python Jscanner.py -u "https://example.com/xxxxx" -f path.txt
```

.........

可以看看工具[ParamScanner](https://github.com/hmx222/ParamScanner) ，后续Jscanner也会以burp插件的形式进行发布（当然python版本也会更新）


写于2023.6.4
