## GeeTest滑块验证码offline模式的破解  
GeeTest滑块验证码通过机器学习检查鼠标行为轨迹，识别人工或机器行为。  
online在线验证的流程，目前最全面的分析文档详见 [https://zhuanlan.zhihu.com/windev](https://zhuanlan.zhihu.com/windev) 。  
online模式的验证流程，网站后台与GeeTest后台 [http://api.geetest.com](http://api.geetest.com) 进行通讯验证。浏览器前端仅做数据采集和简单加密传输。  
offline模式的离线验证，网站后台自行验证，GeeTest后台 [http://static.geetest.com](http://static.geetest.com) 仅提供滑块验证码图片下载功能。浏览器前端做数据采集和本地验证。  
在安全性上，online模式相对非常可靠，offline模式仅仅是障眼法。  
  
### 1. 测试网站  
以[国家企业信用信息公示系统](http://www.gsxt.gov.cn)为例：  
主站使用geetest 5.10.10 online 在线验证模式。各省市站点使用的版本和模块略有差异。  
**geetest offline 5.9.0**  
+ 上海
+ 河北
+ 内蒙古
+ 辽宁
+ 福建
+ 山东
+ 广东
+ 海南
+ 湖北
+ 湖南
+ 四川
+ 云南
+ 西藏
+ 青海
+ 宁夏
  
**geetest offline 5.10.10**  
+ 贵州
+ 陕西
  
### 2. offline模式验证流程  
以上海站点为例 [http://sh.gsxt.gov.cn](http://sh.gsxt.gov.cn)  
#### 2.1 GET 首页 http://sh.gsxt.gov.cn/notice/  
返回HTML页面，解析得到session.token。  
#### 2.2 GET register http://sh.gsxt.gov.cn/notice/pc-geetest/register  
返回JSON数据  
```
{
    "success":0,
    "gt":"39134c54afef1e0b19228627406614e9",
    "challenge":"d2ddea18f00665ce8623e36bd4e3c7c543"
}
```
success = 0 表示启用 offline 验证模式。  
#### 2.3 POST http://sh.gsxt.gov.cn/notice/security/verify_ip  
返回200 True，表示成功。  
#### 2.4 POST http://sh.gsxt.gov.cn/notice/security/verify_keyword  
返回200 True，表示成功。  
#### 2.5 POST http://sh.gsxt.gov.cn/notice/pc-geetest/validate  
上传滑块验证码的本地验证结果数据，简称validate。返回JSON数据  
```
{
    "status":"success",
    "version":"3.3.0"
}
```  
offline模式，后台根本不知道浏览器使用哪张滑块验证码图片，只知道浏览器上传了验证结果的数据。所以完全可以省略下载验证码图片，进行图像识别，计算滑块移动位置，模拟鼠标滑动轨迹这些步骤。   
**验证数据的格式**  
例如：1517aab3f_51aa460f_75555a6a38，其中以_分隔的3段数据是由geetest.5.x.x.js中的distance, rand0, rand1加密混淆得到。  
具体加密过程分析详见 [寻找阿登高地——爬虫工程师如何绕过验证码](http://www.jianshu.com/p/5b6fb04ea686) 。  
其实不用关心加密算法的实现细节，只需找到JavaScript调用入口，传入参数执行即可：  
```
function userresponse(a, b) {
        for (var c = b.slice(32), d = [], e = 0; e < c.length; e++) {
            var f = c.charCodeAt(e);
            d[e] = f > 57 ? f - 87 : f - 48
        }
        c = 36 * d[0] + d[1];
        var g = Math.round(a) + c; b = b.slice(0, 32);
        var h, i = [ [], [], [], [], [] ], j = {}, k = 0; e = 0;
        for (var l = b.length; e < l; e++)
            h = b.charAt(e), j[h] || (j[h] = 1, i[k].push(h), k++, k = 5 == k ? 0 : k);
        for (var m, n = g, o = 4, p = "", q = [1, 2, 5, 10, 50]; n > 0;)
            n - q[o] >= 0 ? (m = parseInt(Math.random() * i[o].length, 10), p += i[o][m], n -= q[o]) : (i.splice(o, 1), q.splice(o, 1), o -= 1);
        return p
    }
```
**3个参数的正确生成**  
distance，rand0，rand1，这3个参数都是随机生成，但是如果写代码直接随机生成，会发现验证成功率不高，那么这3个参数之间存在什么隐藏关联关系？后台是如何校验这3个随机数的正确性？  
其实它们之间存在什么关系不重要，重要的是能够成功通过验证。  
只需人工采样N次，构造足够的样本数组，每次随机选取1个，调用JavaScript加密方法，得到验证数据即可。  
#### 2.6 POST http://sh.gsxt.gov.cn/notice/search/ent_info_list  
上传session.token（步骤1获得），challenge（步骤2获得），validate（步骤5计算），keyword（查询关键字），返回HTML页面，解析DOM结构，即可获得查询结果和session.token的更新（用于下一次查询）。
### 3. Demo Source Code
[GitHub](https://github.com/9468305/script/tree/master/geetest_offline), python 2.7.13  
Install：  
```
pip install requests # HTTP库
pip install PyExecJS # Python调用JavaScript, 配合node.js更佳
pip install beautifulsoup4 # 解析HTML页面
```
Run demo：  
```
python ./gsxt_shanghai.py
python ./gsxt_hebei.py
python ./gsxt_neimenggu.py
```
Implementation：    
[geetest_offline.py](/geetest_offline/geetest_offline.py)  for shanghai， hebei。  
[geetest_offline_nm.py](/geetest_offline/geetest_offline_nm.py) for neimenggu， HTTP Request&Response 略有不同。  
