# -*- coding: utf-8 -*-
import time
import csv
import os
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

LAGOU_URL = 'https://www.lagou.com/gongsi/j%d.html'
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

SLEEPTIME = 3

class JobInfo:
    def __init__(self, company, filter, title, salaryMin, salaryMax, exp, edu):
        self.company = company
        self.filter = filter
        self.title = title
        self.salary_min = salaryMin
        self.salary_max = salaryMax
        self.exp = exp
        self.edu = edu

    @staticmethod
    def header():
        return ["公司", "类别", "职位", "薪酬区间低", "薪酬区间高", "经验要求", "学历要求"]

    def array(self):
        return [self.company, self.filter, self.title, self.salary_min, self.salary_max, self.exp, self.edu]


def lagouPage(browser, jobList, companyName, jobFilter):
    con_list_item = WebDriverWait(browser, SLEEPTIME).until(lambda x: x.find_elements_by_class_name("con_list_item"))
    for item in con_list_item:
        job = item.text.split('\n')
        job_title = job[0]
        #job_date = job[1]
        job_salary = job[2].split('-')
        job_salary_min = job_salary[0]
        if len(job_salary) > 1:
            job_salary_max = job_salary[1]
        else:
            job_salary_max = job_salary[0]
        job_desc = job[3].split('/')
        job_exp = job_desc[0]
        if ' ' in job_exp:
            job_exp = job_exp.strip(' ')
        if '经验' in job_exp:
            job_exp = job_exp.lstrip('经验')
        job_edu = job_desc[1]
        if ' ' in job_edu:
            job_edu = job_edu.strip(' ')

        jobList.append(JobInfo(companyName, jobFilter, job_title, job_salary_min, job_salary_max, job_exp, job_edu))
        print(job_title)
        print(job_salary_min)
        print(job_salary_max)
        print(job_exp)
        print(job_edu)

def getNextSpan(spans):
    for span in spans:
        print(span.text)
        if span.text == '下一页':
            if span.get_attribute('class') == 'next':
                return span
    return None

def lagouFilter(browser, jobList, companyName, jobFilter):
    while True:
        lagouPage(browser, jobList, companyName, jobFilter)
        #check next page
        try:
            pages = browser.find_element_by_class_name('pages')
            spans = pages.find_elements_by_tag_name('span')
            span = getNextSpan(spans)
            if span is not None:
                span.click()
                time.sleep(SLEEPTIME)
            else:
                return
        except NoSuchElementException as e:
            print(e)
            return


def lagouCompany(browser, companyName, companyNumber):
    companyURL = LAGOU_URL % int(companyNumber)
    companyJobList = []
    browser.get(companyURL)
    time.sleep(SLEEPTIME*3)
    while True:
        try:
            print(browser.title)
            con_filter_li = WebDriverWait(browser, SLEEPTIME).until(lambda x: x.find_elements_by_class_name("con_filter_li"))
            for li in con_filter_li:
                print(li.text)
                if li.text == '全部':
                    print("skip")
                    continue
                li.click()
                time.sleep(SLEEPTIME)
                lagouFilter(browser, companyJobList, companyName, li.text)
        except NoSuchElementException as e:
            print(e)
            companyJobList.clear()
            browser.refresh()
            time.sleep(SLEEPTIME*3)
        else:
            #save result to company file
            saveFile = os.path.join(os.getcwd(), companyName + '.csv')
            with open(saveFile, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(JobInfo.header())
                for job in companyJobList:
                    writer.writerow(job.array())
            return


def lagou(browser, companyNumber):
    print("lagou start")
    for k, v in COMPANY.items():
        if companyNumber is not None:
            if int(v) == int(companyNumber):
                lagouCompany(browser, k, v)
                break
        else:
            lagouCompany(browser, k, v)
    print("lagou end")


if __name__ == "__main__":
    _browser = webdriver.Chrome()
    #implicitly_wait seems can not wait until ajax loading complete
    #_browser.implicitly_wait(TIMEOUT)
    singleCompany = None
    if len(sys.argv) > 1:
        singleCompany = sys.argv[1]
    lagou(_browser, singleCompany)
    _browser.quit()
