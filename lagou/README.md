关于拉勾网数据采集爬虫的文章，网上已经写烂了。这里简单记录一个之前帮助同事妹子写的小爬虫工具。  
某天，HR同事妹子接到一个任务，收集并分析拉勾网BAT三家公司所有招聘岗位的分类，要求，薪酬范围，人数等信息。  
人肉采集辛苦枯燥，随手写段代码搭救妹子。

### 开始

拉勾网页面可能改版，以下代码实现可能已失效，不考虑持续维护更新。  
拉勾网给每家注册公司分配一个数字，URL形式是：  

```Python
LAGOU_URL = r'https://www.lagou.com/gongsi/j%d.html'
```

人肉筛选目标公司如下：  

```Python
COMPANY = {
    '腾讯': 451,
    '阿里优酷': 1914,
    '阿里高德': 91,
    '阿里天猫': 52840,
    '阿里UC': 2202,
    '阿里神马搜索': 90948,
    '百度': 1575,
    '百度外卖': 104601
    }
```

每家公司子页面的实现，使用了较多复杂Javascript代码和框架，因此不采用抓包分析HTTP协议的方案。  
简单粗暴直接的组合： Selenium + WebDriver + Chrome。

### Selenium

官网 http://www.seleniumhq.org/  
GitHub https://github.com/SeleniumHQ/selenium  
文档 http://selenium-python.readthedocs.io/  

### ChromeDriver

[ChromeDriver - WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/)  
为什么不使用运行效率更高的 [PhantomJS](http://phantomjs.org/) ？  
因为需要频繁调试代码和观察运行情况。稳定运行后可以随时修改一行代码参数，替换成 PhantomJS 。  
**Chrome 59 beta 开始支持 Headless。** 详见 [Getting Started with Headless Chrome](https://developers.google.com/web/updates/2017/04/headless-chrome)。所以以后应该也不再需要 PhantomJS 了。  

### 数据定义

继续简单粗暴直接：(参数有点多，PyLint 报 Warning 了，无视吧。)  

```Python
class JobInfo(object):
    '''Job Info Object'''
    def __init__(self, company, job_filter, title, salary_min, salary_max, exp, edu):
        self.company = company
        self.filter = job_filter
        self.title = title
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.exp = exp
        self.edu = edu

    @staticmethod
    def header():
        '''csv file header'''
        return ['公司', '类别', '职位', '薪酬区间低', '薪酬区间高', '经验要求', '学历要求']

    def array(self):
        '''object to array'''
        return [self.company,
                self.filter,
                self.title,
                self.salary_min,
                self.salary_max,
                self.exp,
                self.edu]
```

### 页面加载解析

WebDriver API 方便好用强大。  

```Python
con_list_item = WebDriverWait(browser, SLEEPTIME).until(lambda x: x.find_elements_by_class_name('con_list_item'))
```

执行点击翻页跳转

```Python
try:
    pages = browser.find_element_by_class_name('pages')
    spans = pages.find_elements_by_tag_name('span')
    span = get_next_span(spans)
    if span:
        span.click()
        time.sleep(SLEEPTIME)
except NoSuchElementException as _e:
    print(_e)
```

**数据采集完成后写入csv文件，略。**

### 坑

WebDriver API 简单易用，但超时处理机制仍不完善。  

```Python
browser = webdriver.Chrome()
browser.get(url)
browser.refresh()
browser.quit()
```

`implicitly_wait()` 无法判断页面内部各种Ajax操作执行完成的时机。只好注释掉这一行代码。

```Python
browser.implicitly_wait(TIMEOUT)
```
