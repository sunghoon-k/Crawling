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

import pandas as pd

import sqlite3

import requests
import bs4

###############################################################################
# 데이터베이스 세팅 ############################################################
con3 = sqlite3.connect('post3_thema.db')
con4 = sqlite3.connect('post4_KOSPI.db')
con5 = sqlite3.connect('post5_KOSDAQ.db')
con6 = sqlite3.connect('post6_upperLimit.db')

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

for i in range(1):
    # 다음 페이지 클릭
    num = driver.find_elements_by_css_selector("li.num")[i+1]
    driver.execute_script("arguments[0].click()", num)

    # 날짜 체크!
    date_raw = driver.find_element_by_css_selector('div.dateCon')
    date_raw_list = date_raw.get_attribute('innerText').replace('.', '').split(' ')
    date = date_raw_list[0] + date_raw_list[1] + date_raw_list[2]

    # 증시요약(6) - 특징 상한가 및 급등종목
    # 증시요약(5) - 특징 종목(코스닥)
    # 증시요약(4) - 특징 종목(코스피)
    # 증시요약(3) - 특징 테마
    
    # 일단 증시요약(6)만 다운받자
    # 수동으로 해야됨
    # tr과 td로 구분해서 pd.DataFrame 구성해야됨. 
    for j in range(1):
        post = driver.find_element_by_xpath(f'//*[@id="list_Board"]/div[2]/article/div/table/tbody/tr[{5+j}]/th[1]/td/div[1]/span[{5+j}]/span')
        driver.execute_script("arguments[0].click()", post)
        
        res = driver.find_elements_by_css_selector('div.txtCon.resHtml')
        type(res[0].get_attribute('innerText'))
        
        res = driver.find_elements_by_css_selector('table.tbl')
        res = driver.find_elements_by_css_selector('div.txtCon.resHtml')

        len(res)
        for re in res:
            pd.read_html(re.get_attribute('innerText'))
            
        for table in tables:
            pd.DataFrame(table)

        res=requests.get(url=driver.current_url, headers=headers)
        # 한글 깨짐 처리
        # ref: http://pythonstudy.xyz/python/article/403-%ED%8C%8C%EC%9D%B4%EC%8D%AC-Web-Scraping
        res.encoding
        res.raise_for_status() 
        res.encoding=None   # None 으로 설정

        df_list = pd.read_html(res.text)
        for df in df_list:
            print(df)

# nextPage = driver.find_element_by_css_selector('li.last')
# driver.execute_script("arguments[0].click()", nextPage)