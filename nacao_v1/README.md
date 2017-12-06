这次的爬虫目标网站是全国组织机构代码管理中心 http://www.nacao.org.cn 。  
搜索关键字是公司中文名称，搜索结果是公司对应的统一社会信用代码（税号）。  
代码实现非常简单，仅需2个HTTP请求，1个搜索公司列表，1个分页查询结果。  
动手编码之前，先来看看该网站的前端设计实现，有哪些值得吐槽的技术点。  

### 槽点1：网站开放服务时间 每天12小时
>重要公告：网站核查平台服务时间为7*12小时（即每天8:00-20:00）

[知乎：为什么全国组织机构代码管理中心网站（www.nacao.org.cn）只在上班时间开放查询呢？](https://www.zhihu.com/question/33204926)  
网站页面Javascript代码直接写死时间判断逻辑，超出规定时间就直接报错。而服务器始终正常运行。  
第一期，技术人员直接调用浏览器系统时间进行拦截判断。然后用户学会了修改电脑时间。  
第二期，技术人员使用服务器时间进行拦截判断。然后用户学会了绕过Javascript验证。  
第三期，技术人员直接注释了前端Javascript拦截代码。（服务器是否拦截判断，未核实。）  

### 槽点2：信息核查系统 vs 信息校核结果公示系统
首页从上至下，分为2个查询系统。  
第一个是`全国统一社会信用代码信息核查系统`。输入关键字，弹出英文字母图片验证码。  
第二个是`全国统一社会信用代码信息校核结果公示系统`。输入关键字，直接跳转结果页面！！！  
查询数据结果对比，基本一致。那么谁还去用第一个图片验证码系统？？？  
多次测试后发现，第一个系统还有IP反爬机制，一旦封禁，3工作日解封。第二个系统任意使用无限制。  
```
IP被封怎么办？
    本网站核查平台是为公众基于统一社会信用代码信息的一般性核查设立的，不支持大量且频繁的查询请求，如查询过程中出现下图 所示，说明您的查询过于频繁，系统已经对您进行了查询限制，限制期为3个工作日。请于限制期后再访问系统进行查询。
```

### 槽点3：存在疑似SQL注入漏洞
在分析SQL注入漏洞之前，先来看看系统2的爬虫实现，即HTTP参数的含义解释。  
1. 关键字查询  
GET http://125.35.63.141:8080/PublicNotificationWeb/search.do  
参数：searchText = 关键字，searchType = 3。  
响应：返回一个字符串Referer。  
2. 分页获取数据  
POST http://125.35.63.141:8080/PublicNotificationWeb/query.do  
参数：  
```
_params = [ ('pageSize', 20),
            ('searchText', keyword),
            ('searchType', 3),
            ('DJBMBM', ''),
            ('sortField', ''),
            ('currentPage', 1)]
```
含义：  
+ pageSize 分页数据量，默认20，实测可以改成100。即一页返回100项数据。
+ searchText 搜索关键字
+ searchType 搜索类型，固定=3
+ DJBMBM 未知，固定为空
+ sortField 未知，固定为空
+ currentPage 当前分页索引，实测最多5页，值范围0-4。

响应：返回一个JSON字符串。  
+ totalPage 总页数，最大5页。
+ foundCount 总共查询结果数量
+ dataList JSON数组
+ JGMC 公司名称
+ TYSHXYDM 统一社会信用代码（税号）
  
至此，爬虫已经实现完毕。接下来探索每个参数的可能性。  
+ pageSize 从20改成100，最多可一次获得500条数据。
+ searchText 搜索关键字改成*，可获得服务器数据库默认排序数据。此时foundCount等于官网数据库数据总量。
  
实测数据日志见[sql_injection.txt](https://github.com/9468305/script/tree/master/nacao_v1/sql_injection.txt)。  
所以这里能否使用SQLInjection，获得数据库访问权限，直接拖库呢？  
留待有心人探索。  
最后，[V1.0源码见GitHub](https://github.com/9468305/script/tree/master/nacao_v1)。  

### 后记
官网进行了改版，原方案接口失效。新方案V2.0见:  
https://github.com/9468305/script/tree/master/nacao_v2  
