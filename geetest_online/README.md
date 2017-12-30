### GeeTest滑块验证码online模式的破解
继续以[国家企业信用信息公示系统](http://www.gsxt.gov.cn)为例。  
补充一个完成度80%的项目和文档。代码实现主要参考[https://zhuanlan.zhihu.com/windev](https://zhuanlan.zhihu.com/windev)的相关分析文章。  
已实现以下功能：  

#### 1. 所有HTTP Request & Response协议
使用Requests库实现。

#### 2. 验证码图片的拼图重组和识别
使用Pillow库，实现滑块拼图位置的精确定位。  
全局变量`IMAGE_DEBUG`，实现不同精准度的图片本地临时文件存储，以便观察定位效果和改进。  

#### 3. GeeTest Javascript 加解密算法破解
使用PyExecJS库，执行GeeTest Javascript方法，获得正确的明文和密文。  
配合NodeJS使用更佳。  

#### 4. 使用BeautifulSoup库，进行网页数据解析

#### 未完成的20%包括2部分。  
+ 完善用户鼠标轨迹运行的数据仿真算法。
+ 补全官网针对爬虫返回HTTP 521的处理，补全Cookie校验逻辑。

#### 源码见GitHub
https://github.com/9468305/script/tree/master/geetest_online  
