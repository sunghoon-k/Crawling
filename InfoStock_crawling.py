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

# page source 를 1000자까지 출력해보자
print(driver.page_source[:1000])

# driver.quit()