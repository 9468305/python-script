书接前文，全国组织机构代码管理中心 http://www.nacao.org.cn 网站改版，V1.0方案已失效。  
继续分析这次改版的变化，以及V2.0方案的实现。  
V1.0方案见 https://github.com/9468305/script/tree/master/nacao_v1 。
### IP变域名
125.35.63.141:8080 变成 dmedu.org.cn 。（该域名解析IP仍是 125.35.63.141 ）因此2个API接口改变。  
旧：  
http://125.35.63.141:8080/PublicNotificationWeb/search.do  
http://125.35.63.141:8080/PublicNotificationWeb/query.do  
新：  
http://www.dmedu.org.cn/search.do  
http://www.dmedu.org.cn/query.do  

### search.do可绕过
search.do接口返回一个字符串Referer，用于query.do的HTTP Header参数。实测不再需要，直接调用query.do，Referer空值。  

### 参数一致
V1.0和V2.0参数没有变化。  
pageSize 20扩大至100 继续可用  
searchText使用*通配符，继续可用  

### 实现
因此V2.0的代码更简单，源码见GitHub  
https://github.com/9468305/script/tree/master/nacao_v2  

### 后记
目前官网已经针对该接口增加了图片字符验证码，因此该方案已失效。关于如何识别图片字符验证码，可以Google“远程打码”。  
