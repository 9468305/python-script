# -*- coding: utf-8 -*-
'''spider for https://www.lagou.com'''

import time
import csv
import os
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

LAGOU_URL = r'https://www.lagou.com/gongsi/j%d.html'
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

SLEEPTIME = 3 #seconds

class JobInfo(object):
    '''Job Object'''
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
        return ["公司", "类别", "职位", "薪酬区间低", "薪酬区间高", "经验要求", "学历要求"]

    def array(self):
        '''object to array'''
        return [self.company,
                self.filter,
                self.title,
                self.salary_min,
                self.salary_max,
                self.exp,
                self.edu]


def lagou_page(browser, job_list, company_name, job_filter):
    '''filter for every page'''
    con_list_item = WebDriverWait(browser, SLEEPTIME)\
        .until(lambda x: x.find_elements_by_class_name("con_list_item"))
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

        job = JobInfo(company_name,
                      job_filter,
                      job_title,
                      job_salary_min,
                      job_salary_max,
                      job_exp,
                      job_edu)
        job_list.append(job)
        print job_title
        print job_salary_min
        print job_salary_max
        print job_exp
        print job_edu


def get_next_span(spans):
    '''find next page button'''
    for span in spans:
        print span.text
        if span.text == '下一页':
            if span.get_attribute('class') == 'next':
                return span
    return None

def lagou_filter(browser, job_list, company_name, job_filter):
    '''filter by job types'''
    while True:
        lagou_page(browser, job_list, company_name, job_filter)
        #check next page
        try:
            pages = browser.find_element_by_class_name('pages')
            spans = pages.find_elements_by_tag_name('span')
            span = get_next_span(spans)
            if span is not None:
                span.click()
                time.sleep(SLEEPTIME)
            else:
                return
        except NoSuchElementException as no_such_element_exp:
            print no_such_element_exp
            return


def lagou_company(browser, company_name, company_number):
    '''filter for certain company'''
    company_url = LAGOU_URL % int(company_number)
    company_job_list = []
    browser.get(company_url)
    time.sleep(SLEEPTIME*3)
    while True:
        try:
            print browser.title
            con_filter_li = WebDriverWait(browser, SLEEPTIME)\
                .until(lambda x: x.find_elements_by_class_name("con_filter_li"))
            for line in con_filter_li:
                print line.text
                if line.text == '全部':
                    print "skip"
                    continue
                line.click()
                time.sleep(SLEEPTIME)
                lagou_filter(browser, company_job_list, company_name, line.text)
        except NoSuchElementException as no_such_element_exp:
            print no_such_element_exp
            del company_job_list[:]
            # company_job_list.clear() only work for python3
            browser.refresh()
            time.sleep(SLEEPTIME*3)
        else:
            #save result to company file
            save_file = os.path.join(os.getcwd(), company_name + '.csv')
            with open(save_file, 'w', newline='') as save_file_handler:
                writer = csv.writer(save_file_handler)
                writer.writerow(JobInfo.header())
                for job in company_job_list:
                    writer.writerow(job.array())
            return


def lagou(browser, company_number):
    '''lagou entity: target one company or all.'''
    print "lagou start"
    for name, code in COMPANY.items():
        if company_number is not None:
            if int(code) == int(company_number):
                lagou_company(browser, name, code)
                break
        else:
            lagou_company(browser, name, code)
    print "lagou end"


if __name__ == "__main__":
    BROWSER = webdriver.Chrome()
    #implicitly_wait seems can not waiting for Ajax loading complete
    #_browser.implicitly_wait(TIMEOUT)
    SINGLE_COMPANY = None
    if len(sys.argv) > 1:
        SINGLE_COMPANY = sys.argv[1]
    lagou(BROWSER, SINGLE_COMPANY)
    BROWSER.quit()
