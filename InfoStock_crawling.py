# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 22:29:06 2024

@author: kshoo
"""

""" 참고
유튜버 [프로그래머 김플 스튜디오] - "파이썬 셀레니움(selenium) 크롬 드라이버 설치없이 webdriver_manager로 자동설치, 버전 관리"
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import pandas as pd
import numpy as np

import sqlite3

import requests
import bs4

import re

###############################################################################
# 함수 모음 ####################################################################
# 증시요약(6) 특징 상한가 및 급등종목 크롤링 함수 
def crawl6(arg_driver, arg_date, arg_con):

    # 개발 중간 확인용
    # arg_driver = driver
    # arg_date = date
    # arg_con = con6
    
    table = arg_driver.find_elements_by_css_selector('table.tbl')

    columns = ['name', 'code', 'price', 'fluctuation', 'upperLimit_streak', 'reason']
    df6 = pd.DataFrame(columns=columns)
    # 증시요약(6)는 테이블이 1개!
    trList = table[0].find_elements_by_css_selector('tr')
    # trList[0].get_attribute('innerText')
    # trList[1].get_attribute('innerText')
    for lineNum in range(2, len(trList)):
        # print(lineNum)
    
        # 2번부터 테이블 내용임
        # trList[2].get_attribute('innerText')
        contents = trList[lineNum].find_elements_by_css_selector('td')
        # test 출력
        # for element in trList[lineNum].find_elements_by_css_selector('td'):
        #     print(element.get_attribute('innerText'))
        #     print("###################")
        
        # line1: 종목명/종목코드/가격/등락률
        # contents[0].get_attribute('innerText').split('\n')
        name = contents[0].get_attribute('innerText').split('\n')[0] # 1. 종목명

        pattern = r'[^0-9]'
        code = re.sub(pattern, '', contents[0].get_attribute('innerText').split('\n')[1])  
        price = re.sub(pattern, '', contents[0].get_attribute('innerText').split('\n')[2])  
        
        pattern = r'[+%()]'
        fluctuation = re.sub(pattern, '', contents[0].get_attribute('innerText').split('\n')[3])  

        # line2: 상한가 일수
        if contents[1].get_attribute('innerText') == '':
            upperLimit_streak = 0
        else:
            upperLimit_streak = contents[1].get_attribute('innerText')
        
        # line3: 상한가 사유
        reason = contents[2].get_attribute('innerText')

        # 각 내용을 하나의 리스트로 만들기
        line = [name, code, price, fluctuation, upperLimit_streak, reason]
        
        ''' list 를 데이터프레임에 추가하기
        ref: https://emilkwak.github.io/dataframe-list-row-append-ignore-index
        '''
        # df6 = df6.append(pd.Series(line), ignore_index=True) # 이렇게 짜면 새로운 컬럼에 저장한다. 
        df6 = df6.append(pd.Series(line, index=df6.columns), ignore_index=True)

    df6.to_sql(arg_date, con=arg_con, index=False)
    arg_con.commit()
    
# 증시요약(3) 특징 테마 
def crawl3(arg_driver, arg_date, arg_con):    
    table = arg_driver.find_elements_by_css_selector('table.tbl')
    
    # columns = ['특징테마', '이슈요약']
    df3 = pd.DataFrame() # columns=columns
    # 증시요약(6)는 테이블이 1개!
    trList = table[0].find_elements_by_css_selector('tr')
    # trList[0].get_attribute('innerText')
    # trList[1].get_attribute('innerText')
    
    contents = trList[1].find_elements_by_css_selector('td')
    df3['테마시황'] = contents[1].get_attribute('innerText').split('\n\n')

    # 주! 1번줄과 2~n번줄까지 양식이 다름!

    for lineNum in range(2, len(trList), 2):
        # print(lineNum)
        contents1 = trList[lineNum].find_elements_by_css_selector('td')
        theme = contents1[0].get_attribute('innerText')
        line = [contents1[1].get_attribute('innerText')]
        
        contents2 = trList[lineNum+1].find_elements_by_css_selector('td')
        line.extend(contents2[0].get_attribute('innerText').split('\n\n'))
        
        if len(line) > len(df3):
            df3 = df3.reindex(range(len(line)))
        elif len(line) < len(df3):
            line = line + [np.nan] * (len(df3) - len(line))
        
        # 새 컬럼 추가
        df3[theme] = line

    df3.to_sql(arg_date, con=arg_con, index=False)
    arg_con.commit()

# 증시요약 클릭하고 날짜 가져오기
def click_and_getDate(arg_num, arg_driver):
    post = arg_driver.find_element_by_xpath(f'//*[@id="list_Board"]/div[2]/article/div/table/tbody/tr[{11-arg_num}]/th[1]/td/div[1]/span[{11-arg_num}]/span')
    arg_driver.execute_script("arguments[0].click()", post) # 증시요약(arg_num) 클릭
    time.sleep(1)

    # 날짜 체크!
    date_raw = arg_driver.find_element_by_css_selector('div.dateCon')
    date_raw_list = date_raw.get_attribute('innerText').replace('.', '').split(' ')
    date = date_raw_list[0] + date_raw_list[1] + date_raw_list[2]
    print(f"summary{arg_num}, date: "+date)
    time.sleep(0.5)
    
    return date

###############################################################################
# 데이터베이스 세팅 ############################################################
con3 = sqlite3.connect('D:\Stock\상한가 크롤링\post3_thema.db')
# con4 = sqlite3.connect('D:\Stock\상한가 크롤링\post4_KOSPI.db')
# con5 = sqlite3.connect('D:\Stock\상한가 크롤링\post5_KOSDAQ.db')
con6 = sqlite3.connect('D:\Stock\상한가 크롤링\post6_upperLimit.db')

###############################################################################
# headers 세팅 ################################################################
headers={
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
  'Cache-Control': 'max-age=0',
  'Referer': 'https://www.google.com/',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

########################################################################################################
# Options() 설명 #######################################################################################
options = Options()

# user_agent: 우리가 사용하는 브라우저가 기본적으로 가지고 있는 정보
# 사용하는 이유: 사이트에 따라 정보가 이상하면 차단당할 위험이 있다. 
# 확인하는 방법: https://useragentstring.com/
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# user data를 사용하면 방문기록을 남길 수 있다. 
# 즉, 크롤링하면서 방문한 사이트를 확인할 수 있다. 
# 저장할 경로를 입력하면 된다. 
# 매번 새롭게 시행하려면 user data 옵션을 넣지 않으면 된다. 
user_data = "D:\\Stock\\상한가 크롤링"

options.add_argument(f"user-agent={user_agent}")
# options.add_argument(f"user-data-dir={user_data}")

# 브라우저 바로 닫힘 방지
options.add_experimental_option("detach", True) 

# 최대화 화면으로 시작
options.add_argument("--start-maximized")
# F11 을 눌러서 전체 화면으로 시작
# options.add_argument("--start-maximized")
# 창크기 설정
# options.add_argument("window-size=500,500")

# 우리 눈에 보이지 않게 셀레니움 사용(백그라운드에서 실행)
# 클릭이나 검색도 가능하다!
# options.add_argument("--headless")
# 주로 headless 와 함께 사용
# headless 만으로 작동이 잘 안되는 경우 사용하는 코드
# options.add_argument("--disable-gpu")

# 음소거 시행
# options.add_argument("--mute-audio")
# 시크릿 모드로 시행
# options.add_argument("incognito")

# 불필요한 메세지 출력 방지
# 터미널에서 관련없는 메세지 출력되는 것 방지
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# '자동화된 테스트 소프트웨어' 메세지 제거
options.add_experimental_option("excludeSwitches", ["enable-automation"])

##############################################################################################################
# webdriver 사용 #############################################################################################
# 이전에 webdriver 사용 방법
# 자신의 버전에 맞는 chromedriver 를 다운 받아서 경로를 입력하여 사용
# driver = webdriver.Chrome("104/chromedriver.exe", options=options)

# 크롬이 업데이트되면 계속 크롬드라이버도 업데이트 했어야 했다. 
# 이를 자동화 하는 것이 webdriver_manager 모듈이다. 
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
''' 위 코드를 아래와 같이 분리해서 사용할 수 있다.
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service, options=options)
'''
chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver, options=options)

# service 기능 사용할 수 없음. 이유는 아직 몰?루
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=options)

# 크롤링을 원하는 사이트 오픈!
# driver.get('https://www.naver.com/')
driver.get('https://new.infostock.co.kr/MarketNews/TodaySummary')

###############################################################################
# element not interactable 오류!
# ref1: https://stackoverflow.com/questions/65064715/how-to-change-the-date-of-a-hidden-element-of-a-datepicker-using-setattribute-me
# ref2: https://shawn-dev.oopy.io/af79811b-2432-42ee-b2dc-b1fcf9a21d23
page_num = 1

WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, 'li.num'))

cursor = con6.cursor()
while(1):
    # 현재 페이지 확인
    currentPage = int(driver.find_element_by_css_selector("li.num.current").get_attribute("innerText"))

    # 현재 페이지가 마지막이면 next 클릭, 아니면 다음페이지 클릭
    pageClick = currentPage % 5
    if pageClick == 0:
        num = driver.find_element_by_css_selector("li.last")
        driver.execute_script("arguments[0].click()", num)
        time.sleep(2)
    else:        
        # 다음 페이지 클릭
        num = driver.find_elements_by_css_selector("li.num")[pageClick]
        driver.execute_script("arguments[0].click()", num)
    time.sleep(1)

    # len(driver.find_elements_by_css_selector("li.num"))

    # 증시요약(6) - 특징 상한가 및 급등종목
    # 증시요약(5) - 특징 종목(코스닥)
    # 증시요약(4) - 특징 종목(코스피)
    # 증시요약(3) - 특징 테마
    
    # 일단 증시요약(6)만 다운받자
    # 수동으로 해야됨
    # tr과 td로 구분해서 pd.DataFrame 구성해야됨. 

    ###########################################################################
    # 증시요약(6) 크롤링 #######################################################
    # 증시요약(6)을 클릭하고 날짜 가져오기
    date = click_and_getDate(6, driver)

    # if int(date) < 20240101:
    #     break
    
    ###########################################################################
    # 먼저 데이터가 이미 존재하는지 확인 ########################################
    
    # 데이터베이스 커서 연결
    cursor = con6.cursor()
    
    # 데이터베이스에 테이블이 존재하는지 확인
    table_name = date
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    time.sleep(1)

    exists = cursor.fetchone()
    
    if not exists:
        try:
            # 테이블이 존재하지 않으면 크롤링 및 to_sql 실행
            crawl6(driver, date, con6)
            time.sleep(5)

        except Exception as e:
            print(f"Error occurred: {e}")
    else:
        # 테이블이 이미 존재하는 경우, 아무 작업도 수행하지 않음
        print(f"Table '{table_name}' already exists.")
    
    ###########################################################################
    # 증시요약(3) 크롤링 #######################################################
    # 증시요약(3)을 클릭하고 날짜 가져오기
    date = click_and_getDate(3, driver)
    cursor = con3.cursor()
    
    # 데이터베이스에 테이블이 존재하는지 확인
    table_name = date
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    time.sleep(1)

    exists = cursor.fetchone()
    
    if not exists:
        try:
            # 테이블이 존재하지 않으면 크롤링 및 to_sql 실행
            crawl3(driver, date, con3)
            time.sleep(5)

        except Exception as e:
            print(f"Error occurred: {e}")
    else:
        # 테이블이 이미 존재하는 경우, 아무 작업도 수행하지 않음
        print(f"Table '{table_name}' already exists.")

    ###########################################################################
    # 조건 만족하면 크롤링 중단 ################################################    
    if int(date) < 20240101:
        break

    
# 연결 닫기
con6.close()
con3.close()
