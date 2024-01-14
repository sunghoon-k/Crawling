# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 14:31:45 2024

@author: kshoo
"""
''' 인포스탁 당일 자료는 팍스넷에서 가져와야 한다. 
'''
import datetime

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
import json

import re

import pykrx
from pykrx import stock

URL = 'https://www.paxnet.co.kr/search/news?kwd=%EC%A6%9D%EC%8B%9C%EC%9A%94%EC%95%BD&wlog_nsise=search&order=1'

# # 카카오 전송 <- 글자수 200자 제한;;
# kakaoAPI = 'e6c6eb8243b356ca28dfe8394ee7d30e'
# kakaoURL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
# kakaoHEADER = {
#     "Content-Type": "application/x-www-form-urlencoded", 
#     "Authorization": 'Bearer ' + kakaoAPI,
#     'Content-Type': 'application/json; charset=utf-8'}

def send_message(content, URL, HEADER):
    payload = {'content': content}
    response = requests.post(URL, json=payload, headers=HEADER)

    if response.status_code == 200:
        print(f'성공적으로 카카오톡에 전송했습니다.')
    else:
        print(f'전송 실패. HTTP 상태 코드: {response.status_code}')
    time.sleep(1)



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
    
    return df6
    
# 증시요약(3) 특징 테마
def crawl3(arg_driver, arg_date, arg_con):    
    # 개발용 테스트
    # arg_driver = driver
    # arg_date = formatted_recent_business_day
    # arg_con = con3


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
    
    return df6

###############################################################################
# 데이터베이스 세팅 ############################################################
con3 = sqlite3.connect('D:\Stock\상한가 크롤링\post3_thema.db')
# con4 = sqlite3.connect('D:\Stock\상한가 크롤링\post4_KOSPI.db')
# con5 = sqlite3.connect('D:\Stock\상한가 크롤링\post5_KOSDAQ.db')
con6 = sqlite3.connect('D:\Stock\상한가 크롤링\post6_upperLimit.db')


########################################################################################################
# Options() 설명 #######################################################################################
options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")

# 브라우저 바로 닫힘 방지
options.add_experimental_option("detach", True) 

# 최대화 화면으로 시작
options.add_argument("--start-maximized")

# 우리 눈에 보이지 않게 셀레니움 사용(백그라운드에서 실행)
# 클릭이나 검색도 가능하다!
# options.add_argument("--headless")
# 주로 headless 와 함께 사용
# headless 만으로 작동이 잘 안되는 경우 사용하는 코드
# options.add_argument("--disable-gpu")

# 불필요한 메세지 출력 방지
# 터미널에서 관련없는 메세지 출력되는 것 방지
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# '자동화된 테스트 소프트웨어' 메세지 제거
options.add_experimental_option("excludeSwitches", ["enable-automation"])

###############################################################################
# 가장 최근 영업일 구하기 ######################################################
# 오늘 날짜 가져오기
today = datetime.datetime.now()

# 원하는 형식으로 날짜를 문자열로 포맷팅
formatted_today = today.strftime('%Y%m%d')
seven_days_ago = today - datetime.timedelta(days=7)
formatted_seven_days_ago = seven_days_ago.strftime('%Y%m%d')

df = stock.get_index_fundamental(formatted_seven_days_ago, formatted_today, "1001")
recent_business_day = df.index[-1].strftime('%Y.%m.%d')

##############################################################################################################
# webdriver 사용 #############################################################################################
chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver, options=options)
driver.get(URL)
WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, 'ul.thumb-list'))

# "증시요약(3)"이나 "증시요약(6)"을 포함하고 "recent_business_day"와 일치하는 요소 찾기
for element in driver.find_elements_by_css_selector('ul.thumb-list dl'):
    if '증시요약(3)' in element.text and recent_business_day in element.text:
        print(element.text)
        href_attribute3 = element.find_element_by_css_selector('dt a').get_attribute('href')
        # href_attribute를 사용하여 링크로 이동하거나 원하는 작업을 수행할 수 있습니다.
    if '증시요약(6)' in element.text and recent_business_day in element.text:
        print(element.text)
        href_attribute6 = element.find_element_by_css_selector('dt a').get_attribute('href')
        # href_attribute를 사용하여 링크로 이동하거나 원하는 작업을 수행할 수 있습니다.

###############################################################################

formatted_recent_business_day = recent_business_day.replace('.', '')

# 데이터베이스에 테이블이 존재하는지 확인
cursor = con3.cursor()
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{formatted_recent_business_day}';")
time.sleep(1)

exists = cursor.fetchone()

if not exists:
    try:
        # 증시요약(3)으로 이동
        driver.get(href_attribute3)
        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, 'table'))

        # 테이블이 존재하지 않으면 크롤링 및 to_sql 실행
        df3 = crawl3(driver, formatted_recent_business_day, con3)
        time.sleep(5)

    except Exception as e:
        print(f"Error occurred: {e}")
else:
    # 테이블이 이미 존재하는 경우, 아무 작업도 수행하지 않음
    print(f"Table '{formatted_recent_business_day}' already exists.")
    # SQL 쿼리 실행 및 데이터 가져오기
    query = f"SELECT * FROM '{formatted_recent_business_day}';"
    df3 = pd.read_sql_query(query, con3)

con3.close()

###############################################################################

# 데이터베이스에 테이블이 존재하는지 확인
cursor = con6.cursor()
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{formatted_recent_business_day}';")
time.sleep(1)

exists = cursor.fetchone()

if not exists:
    try:
        # 증시요약(6)으로 이동
        driver.get(href_attribute6)
        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, 'table'))
        # 테이블이 존재하지 않으면 크롤링 및 to_sql 실행
        df6 = crawl6(driver, formatted_recent_business_day, con6)
        time.sleep(5)

    except Exception as e:
        print(f"Error occurred: {e}")
else:
    # 테이블이 이미 존재하는 경우, 아무 작업도 수행하지 않음
    print(f"Table '{formatted_recent_business_day}' already exists.")
    # SQL 쿼리 실행 및 데이터 가져오기
    query = f"SELECT * FROM '{formatted_recent_business_day}';"
    df6 = pd.read_sql_query(query, con6)

con6.close()

###############################################################################
# DISCORD 에 전송하기
# 데이터프레임 생성 (이 부분을 실제 데이터프레임 생성 코드로 대체하세요)
# 디스코드 웹훅 URL 설정
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1193504274638983239/JXP41qlsLJzN0_uXCN5BMoBa5x3BcY1_1sRKORxDWYmNRWsQMz05yLbyjI2RuLWLwrhm'

# 데이터프레임을 JSON 문자열로 변환
# df3_json = df3.to_json(orient='records', force_ascii=False)
# df3_json_utf8 = df3_json.encode('utf-8')

# requests.post(DISCORD_WEBHOOK_URL, data=df3_json_utf8)

headers = {'Content-Type': 'application/json; charset=utf-8'}
# response = requests.post(DISCORD_WEBHOOK_URL, data=df3_json_utf8, headers=headers)

# 각 컬럼의 내용을 띄워서 전송
# 각 컬럼의 내용을 띄워서 전송 (None 값 제외)

content = '####################################################################\n'
content += f'**{recent_business_day}증시요약(3) - 특징 테마**:\n\n'
send_message(content, DISCORD_WEBHOOK_URL, headers)

for column in df3.columns:
    content = f'**{column}**:\n\n'
    for value in df3[column].dropna():  # None 값을 제외하고 데이터만 가져오기
        content += f'{value}\n\n'
    content += '\n\n'
    send_message(content, DISCORD_WEBHOOK_URL, headers)


content = '####################################################################\n'
content += f'**{recent_business_day}증시요약(6) - 특징 상한가 및 급등종목**:\n\n'
send_message(content, DISCORD_WEBHOOK_URL, headers)

# 각 행을 한 줄마다 띄워서 전송
for index, row in df6.iterrows():
    content = f'종목{index+1}.####################\n'
    content += f'종목명: {row["name"]}\n'
    content += f'주식가격: {row["price"]}\n'
    content += f'등락률: {row["fluctuation"]}\n'
    content += f'상한가 연속: {row["upperLimit_streak"]}\n'
    content += f'사유: {row["reason"]}\n'
    send_message(content, DISCORD_WEBHOOK_URL, headers)

# ohlcv 가져오기        
# df = stock.get_market_ohlcv("20190720", "20220810", "1001")
