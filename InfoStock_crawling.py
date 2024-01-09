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

options = Options()
options.add_experimental_option('detach', True) # 브라우저 바로 닫힘 방지
options.add_experimental_option('excludeSwitches', ['enable-logging']) # 불필요한 메시지 제거

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
driver.get('https://new.infostock.co.kr/MarketNews/TodaySummary')
