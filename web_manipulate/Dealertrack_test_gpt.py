import os
import re
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import json

# func
def remove_country_code_and_non_digits(input_text):
    """
    입력 텍스트에서 '+1'을 제외하고 숫자가 아닌 텍스트를 제거합니다.

    Args:
        input_text (str): 입력 텍스트
    
    Returns:
        str: 처리된 숫자 문자열
    """
    # '+1' 제거
    if input_text.startswith("+1"):
        input_text = input_text[2:]
    
    # 숫자가 아닌 문자 제거
    cleaned_text = re.sub(r"[^0-9]", "", input_text)
    
    return cleaned_text

# JSON 파일 경로 지정
current_date = datetime.now().strftime('%Y-%m-%d')  # "YYYY-MM-DD" 형식
# file_name = os.path.join(".", "airtable_data", f"table_list_{current_date}.json")
file_name = os.path.join(".", "airtable_data", f"table_list_2024-12-18.json")

# JSON 파일 읽기
with open(file_name, 'r', encoding='utf-8') as file:
    _data = json.load(file)
_data = _data[23]
#######################################################################  Login  ##############################################################################
#############################################################################################################################################################
# .env 파일에서 환경 변수 로드
load_dotenv()
DEALERTRACK_ID = os.getenv("DEALERTRACK_ID")
DEALERTRACK_PASS = os.getenv("DEALERTRACK_PASS")

# URL 설정
login_url = "https://auth.dealertrack.ca/idp/startSSO.ping?PartnerSpId=prod_dtc_sp_pingfed"  # form의 action 속성에서 가져옴
dealertrack_default_url = "https://www.dealertrack.ca/default1.aspx"

# 로그인 정보
username = DEALERTRACK_ID
password = DEALERTRACK_PASS

# POST 요청에 필요한 데이터
login_data = {
    "pf.username": username,
    "pf.pass": password,
    "pf.ok": "",
    "pf.cancel": "",
    "pf.adapterId": "ARTHTMLLOGINPAGE",
}

# 세션 생성 (쿠키 관리용)
session = requests.session()

# 로그인 요청
response = session.post(login_url, data=login_data)
response.raise_for_status()

# 로그인 성공 후 페이지 요청
res = session.get(dealertrack_default_url)
res.raise_for_status()

# BeautifulSoup으로 HTML 내용 확인
soup = BeautifulSoup(res.text, 'html.parser')

options = Options()
options.add_experimental_option("detach", True)
# 크롬 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 웹페이지 로드
driver.get(dealertrack_default_url)

print(f"now started")

# Requests 세션의 쿠키를 Selenium으로 복사
cookies = session.cookies.get_dict()
for name, value in cookies.items():
    driver.add_cookie({'name': name, 'value': value})

# 쿠키를 적용한 후 새로고침
driver.refresh()
driver.get("https://www.dealertrack.ca/DTCanada/Core/application/application_new_type.aspx")

wait = WebDriverWait(driver, 20)

#############################################################  Crate New Application 선택 ######################################################################
################################################################################################################################################################
# "main" 프레임으로 전환
iframe = driver.find_element(By.ID, "iFrm")
driver.switch_to.frame(iframe)
driver.switch_to.frame("main")


### 드롭다운 요소 찾기
# ddAsset에서 'Automotive' 선택 (value="AU")
asset_dropdown_element = wait.until(EC.element_to_be_clickable((By.ID, "ddAsset")))
asset_dropdown = Select(asset_dropdown_element)
asset_dropdown.select_by_value("AU")

# ddLenders에서 'Scotiabank' 선택 (value="BNS")
lenders_dropdown_element = wait.until(EC.element_to_be_clickable((By.ID, "ddLenders")))
lenders_dropdown = Select(lenders_dropdown_element)
lenders_dropdown.select_by_value("BNS")

# ddProduct에서 'Lease' 선택 (value="1")
ddProduct_element = wait.until(EC.element_to_be_clickable((By.ID, "ddProduct")))
product_dropdown = Select(ddProduct_element)
# Print all available options
# for option in product_dropdown.options:
#     print(f"Option text: {option.text}, value: {option.get_attribute('value')}")
product_dropdown.select_by_value("2")

time.sleep(1)

# 'Continue' 버튼 찾기
continue_button = driver.find_element(By.ID, "btnSave")
print(continue_button)
continue_button.click() # 버튼 클릭 (폼 제출)
print("Form submitted successfully!") # 브라우저가 새 페이지로 이동한 후 확인


########################################################### Deal Management page ###############################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################

############################################################### Applicant(s) ###################################################################################
################################################################################################################################################################
################################################################################################################################################################


########################################################### Personal Information ###############################################################################
################################################################################################################################################################

try:
    salutation_dropdown = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl20_ctl00_ddlSalutation"))
    )
    print("salutation_dropdown field is loaded.")
except:
    print("Timeout: salutation_dropdown field was not found.")

# # 드롭다운 요소 찾기
# salutation_dropdown = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlSalutation")

# Selenium의 Select 클래스 사용
select = Select(salutation_dropdown)

if _data["fields"]["Salutation"]=="Dr.":
    # "Mr." 옵션 선택
    select.select_by_visible_text("Dr.")

elif _data["fields"]["Salutation"]=="Mr." or  _data["fields"]["Salutation"]=="Mr":
    # "Mr." 옵션 선택
    select.select_by_visible_text("Mr.")

elif _data["fields"]["Salutation"]=="Ms." or _data["fields"]["Salutation"]=="Ms":
    # "Mr." 옵션 선택
    select.select_by_visible_text("Ms.")

elif _data["fields"]["Salutation"]=="Miss":
    # "Mr." 옵션 선택
    select.select_by_visible_text("Miss")

elif _data["fields"]["Salutation"]=="Mrs.":
    # "Mr." 옵션 선택
    select.select_by_visible_text("Mrs.")
else:
    pass
# 선택한 옵션 확인
selected_option = select.first_selected_option
print(f"Selected option: {selected_option.text}")  # 출력: "Mr."

# First Name 입력 필드 찾기
first_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtFirstName")
first_name_input.send_keys(_data["fields"].get("First Name", ""))

entered_value = first_name_input.get_attribute("value")
print(f"Entered value: {entered_value}")  # 출력: "John"

# Middle Name 입력 필드 찾기
middle_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtMiddleName")

# Middle Name 데이터 입력
middle_name_input.send_keys(_data["fields"].get("Middle Name", ""))
entered_value = middle_name_input.get_attribute("value")
print(f"Entered Middle Name: {entered_value}")  # 출력: "Edward"

# time.sleep(1)
# Last Name 입력 필드 찾기
last_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtLastName")
last_name_input.send_keys(_data["fields"].get("Last Name", ""))

entered_value = last_name_input.get_attribute("value")
print(f"Entered Last Name: {entered_value}")  # 출력: "Smith"

# suffix_dropdown = Select(driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlSuffix"))

################################################################# Number 입력 ####################################################################################
# SIN 입력 필드 요소 찾기
if "SIN" in _data["fields"]:
    sin_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtSIN")
    sin_input.click()
    sin_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

    # SIN 데이터 입력
    _digit = _data["fields"].get("SIN", "")
    # sin_data = "555 555 555"
    if len(_digit) == 9:
        sin_input.send_keys(_data["fields"].get("SIN", ""))
    # 입력 확인
    print(f"SIN Entered: {sin_input.get_attribute('value')}")

# class="MaskedEditFocus" 요소 찾기
phone_field = wait.until(EC.presence_of_element_located((By.ID, "ctl21_ctl20_ctl00_txtPhone")))
phone_field.click()
phone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 전화번호 입력
# phone_number = "4374536013"
if "Phone" in _data["fields"]:
    phone_number = remove_country_code_and_non_digits(_data["fields"]["Phone"])
phone_input.send_keys(phone_number)
print(f"Phone Number Entered: {phone_input.get_attribute('value')}")


# class="MaskedEditFocus" 요소 찾기
mobile_phone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 전화번호 입력
# mobile_phone_number = "4374536003"
if "Phone" in _data["fields"]:
    mobile_phone_number = remove_country_code_and_non_digits(_data["fields"]["Phone"])
mobile_phone_input.send_keys(mobile_phone_number)
print(f"Mobile Phone Number Entered: {mobile_phone_input.get_attribute('value')}")


# Date of Birth :  1987-05-18
date_of_birth = _data["fields"].get("Date of Birth", "")
year, month, day = date_of_birth.split("-")

# class="MaskedEditFocus" 요소 찾기
month_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_MM")

# 월 입력
month_input.send_keys(month)  
print(f"Month Entered: {month_input.get_attribute('value')}")



day_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_DD")
# 일 입력
# day_value  = "6"
day_input.send_keys(day)
print(f"Day Entered: {day_input.get_attribute('value')}")


# class="MaskedEditFocus" 요소 찾기
year_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_YYYY")

# year 입력
# year_value  = "2024"
year_input.send_keys(year)  
print(f"Year Entered: {year_input.get_attribute('value')}")
################################################################################################################################################################## 
# Gender 드롭다운 찾기
gender_select = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlGender")
# 드롭다운을 Select 객체로 변환
select = Select(gender_select)
# "Female" 옵션 선택
if "Gender" in _data["fields"] and _data["fields"]["Gender"]:
    if _data["fields"]["Gender"]=="Male":
        select.select_by_value("MALE")
    elif _data["fields"]["Gender"]=="Female":
        select.select_by_value("FEMALE")
else:
    pass

selected_option = select.first_selected_option
print(f"Selected Gender: {selected_option.text}")

# Marital Status 드롭다운 찾기
marital_status_select = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlMaritalStatus")

# 드롭다운을 Select 객체로 변환
select = Select(marital_status_select)

# "Married" 옵션 선택
if "Marital Status" in _data["fields"] and _data["fields"]["Marital Status"]:
    if _data["fields"]["Marital Status"]=="Married":
        select.select_by_value("MR")
    elif _data["fields"]["Marital Status"]=="Widow / Widower":
        select.select_by_value("WD")
    elif _data["fields"]["Marital Status"]=="Single":
        select.select_by_value("SG")
    elif _data["fields"]["Marital Status"]=="Common Law":
        select.select_by_value("CL")
    elif _data["fields"]["Marital Status"]=="Separated":
        select.select_by_value("SP")
else:
    pass

selected_option = select.first_selected_option
print(f"Selected Marital Status: {selected_option.text}")

# 이메일 입력 필드 찾기
email_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtEmail")
email_input.send_keys(_data["fields"].get("Email", ""))

# 입력된 이메일 값 확인
entered_email = email_input.get_attribute("value")
print(f"Entered Email: {entered_email}")

# 'Language' 드롭다운 찾기
language_dropdown = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlLanguage")

# Select 객체로 드롭다운을 제어
select = Select(language_dropdown)

# 'English' 선택 (value="en-CA")
select.select_by_value("en-CA") # fr-CA

######################################################## Current Address ##################################################################
###########################################################################################################################################
# Suite No : example 3108
# SUITE 3108 , 호텔이나 럭셔리 빌딩
# UNIT 3108 , GENERAL
# 3108-STnumber(107)
# APT 3108 , 큰 방

# Postal Code 입력 필드 찾기
try:
    postal_code_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl21_ctl00_txtPostalCode"))
    )
    print("postal_code_input field is loaded.")
except:
    print("Timeout: postal_code_input field was not found.")

postal_code_input.click()
postal_code_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

# 우편번호 입력
postal_code_input.send_keys(_data["fields"].get("Postal Code", ""))
entered_value = postal_code_input.get_attribute("value")
print(f"Entered Postal Code: {entered_value}")

# 'Address Lookup' 버튼 찾기
address_lookup_button = driver.find_element(By.ID, "ctl21_ctl21_ctl00_btnPostalCodeLookup")
address_lookup_button.click()

# 버튼 클릭 후 결과를 확인할 수 있도록 시간 대기
time.sleep(5)

text = "ST LAURENT"
# iframe로 전환 (VIN Lookup 창이 iframe에 포함되어 있으므로)

try:
    iframe = wait.until(EC.element_to_be_clickable((By.ID, "DTC$ModalPopup$Frame")))
    driver.switch_to.frame(iframe)
    # 테이블 로드 대기
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gvPostalCode")))

    # 테이블 행 가져오기
    rows = driver.find_elements(By.XPATH, "//table[@id='gvPostalCode']/tbody/tr")

    # 첫 번째 행은 헤더이므로 제외하고 반복문 실행
    for row in rows[1:]:
        # 'Street Name' 값 가져오기
        street_name = row.find_element(By.XPATH, "./td[2]").text.strip()
        
        # 비교 값과 일치 여부 확인
        if street_name == text:
            # 라디오 버튼 클릭
            radio_button = row.find_element(By.XPATH, "./td[1]/input[@type='radio']")
            radio_button.click()
            print(f"Radio button for '{text}' clicked.")
            break
    
    else:
        print(f"No matching 'Street Name' found for '{text}'.")

    btnOK = wait.until(EC.element_to_be_clickable((By.ID, "btnOK")))
    # 버튼 클릭
    btnOK.click()

    driver.switch_to.parent_frame()
except:
    pass
    # 브라우저 닫기
    # driver.quit()


# iframe 밖으로 이동

# driver.switch_to.default_content() 는 에러가 발생했음

# 'Duration in Years' 텍스트 필드 요소 찾기
try:
    duration_years_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl21_ctl00_CDurationCurrentAddress_Y"))
    )
    print("Duration field is loaded.")
except:
    print("Timeout: Duration input field was not found.")

# Duration at Current Address
# duration_years_value = "2"
duration_years_input.send_keys(_data["fields"].get("Duration at Current Address", ""))
entered_value = duration_years_input.get_attribute("value")
print(f"Entered Duration in Years: {entered_value}")

# 'Duration in Months' 텍스트 필드 요소 찾기
duration_months_input = driver.find_element(By.ID, "ctl21_ctl21_ctl00_CDurationCurrentAddress_M")
duration_months_value = "6"
duration_months_input.send_keys(duration_months_value)

entered_value = duration_months_input.get_attribute("value")
print(f"Entered Duration in Months: {entered_value}")

######################################################## Previous Address #################################################################
###########################################################################################################################################
# Duration < 2 면 작성

###################################################### Home/Mortgage Details ##############################################################
###########################################################################################################################################
# Housing Status
# Own with Mortgage
# Rent
# Own Free & Clear
# Living with Parents
# 'Home' 드롭다운 요소 찾기
home_dropdown = driver.find_element(By.ID, "ctl21_ctl23_ctl00_ddlHome")

# Selenium의 Select 객체 생성
select = Select(home_dropdown)

# 특정 옵션 선택 (예: 'Own with Mortgage')
# OW : Own with Mortage
# OF : Own Free & Clear
# OM : Own Mobile Home
# RE : Rent
# PA : With parents
# RH : Reserve Housing
# OT : Other
if "Housing Status" in _data["fields"] and _data["fields"]["Housing Status"]:
    if _data["fields"]["Housing Status"]=="Own with Mortgage":
        select.select_by_value("OW")
        # Mortgage Holder
        mortgage_holder_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageHolder")
        mortgage_holder_input.clear()
        mortgage_holder_input.send_keys(_data["fields"].get("Lender", ""))
        entered_value = mortgage_holder_input.get_attribute("value")
        print(f"Entered Mortgage Holder: {entered_value}")

    elif _data["fields"]["Housing Status"]=="Own Free & Clear":
        select.select_by_value("OF")
    elif _data["fields"]["Housing Status"]=="Rent":
        select.select_by_value("RE")
    elif _data["fields"]["Housing Status"]=="Living with Parents":
        select.select_by_value("PA")
else:
    pass

selected_option = select.first_selected_option
print(f"Selected Home Option: {selected_option.text}")

# 'Market Value' 입력 필드 찾기
market_value_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtmarketValue")

# Market Value
market_value_input.clear()
market_value_input.send_keys(_data["fields"].get("Market Value", ""))

entered_value = market_value_input.get_attribute("value")
print(f"Entered Market Value: {entered_value}")

# 'Mortgage Amount' 입력 필드 찾기
mortgage_amount_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageAmount")

# Mortgage Amount
mortgage_amount_input.clear()
market_value_input.send_keys(_data["fields"].get("Mortgage Amount", ""))

entered_value = mortgage_amount_input.get_attribute("value")
print(f"Entered Mortgage Amount: {entered_value}")

# 'Mortgage Holder' 입력 필드 찾기
# Lender
# mortgage_holder_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageHolder")

# 값 입력 (예: 'ABC Bank')
# mortgage_holder = "ABC Bank"
# mortgage_holder_input.clear()  # 기존 값 삭제
# mortgage_holder_input.send_keys(mortgage_holder)

# 입력된 값 확인
# entered_value = mortgage_holder_input.get_attribute("value")
# print(f"Entered Mortgage Holder: {entered_value}")  # 출력: Entered Mortgage Holder: ABC Bank


# 'Monthly Payment' 입력 필드 찾기
monthly_payment_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMonthlyPayment")

# Monthly Payment
monthly_payment_input.clear() 
monthly_payment_input.send_keys(_data["fields"].get("Monthly Payment", ""))

entered_value = monthly_payment_input.get_attribute("value")
print(f"Entered Monthly Payment: {entered_value}")




######################################################## Current Employment ###############################################################
###########################################################################################################################################

# 'Type of Current Employment' 드롭다운 요소 찾기
# Employment Status
current_employment_type_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlTypeCurEmp")

# Selenium의 Select 객체 생성
select_employment_type = Select(current_employment_type_dropdown)

if "Employment Status" in _data["fields"] and _data["fields"]["Employment Status"]:
    if _data["fields"]["Employment Status"]=="At Home":
        select.select_by_value("At home")
        
    elif _data["fields"]["Employment Status"]=="Executive":
        select.select_by_value("Executive")

    elif _data["fields"]["Employment Status"]=="Labourer":
        select.select_by_value("Labourer")

    elif _data["fields"]["Employment Status"]=="Office Staff":
        select.select_by_value("Office Staff")

    elif _data["fields"]["Employment Status"]=="Other":
        select.select_by_value("Other")

    elif _data["fields"]["Employment Status"]=="Production":
        select.select_by_value("Production")

    elif _data["fields"]["Employment Status"]=="Professional":
        select.select_by_value("Professional")

    elif _data["fields"]["Employment Status"]=="Retired":
        select.select_by_value("Retired")

    elif _data["fields"]["Employment Status"]=="Sales":
        select.select_by_value("Sales")

    elif _data["fields"]["Employment Status"]=="Self-Employed":
        select.select_by_value("Self-Employed")

    elif _data["fields"]["Employment Status"]=="Service":
        select.select_by_value("Service")
    
    elif _data["fields"]["Employment Status"]=="Trades":
        select.select_by_value("Trades")
    
    elif _data["fields"]["Employment Status"]=="Student":
        select.select_by_value("Student")

    elif _data["fields"]["Employment Status"]=="Unemployed":
        select.select_by_value("Unemployed")

else:
    pass


# 원하는 옵션 선택 (예: 'Self-Employed')
# At home
# Executive
# Labourer
# Management
# Office Staff
# Other
# Production
# Progessional
# Retired
# Sales
# Self- Employed
# Service
# Student
# Trades
# Unemployed
# employment_type = "Self-Employed"
# select_employment_type.select_by_visible_text(employment_type)

selected_option = select_employment_type.first_selected_option
print(f"Selected Employment Type: {selected_option.text}")

# 'Current Employer' 입력 필드 찾기
# Employer Name
current_employer_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtEmployerCurEmp")
current_employer_input.send_keys(_data["fields"].get("Employer Name", ""))

entered_value = current_employer_input.get_attribute("value")
print(f"Entered Current Employer: {entered_value}")

# 'Employment Status' 드롭다운 요소 찾기
employment_status_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlStatusCurEmp")

# Select 객체 생성
select = Select(employment_status_dropdown)

# 값 선택 (예: 'Full time')
# FT : Full time
# FTP : Full Time (Probation)
# PTC : Part Time (Casual)
# PTR : Part Time (Regular)
# RET : Retired
# SEAS : Seasonal Summer
# SEAW : Seasonal Winter
# SE : Self Employed
employment_status_value = "FT"
current_employer_input.send_keys(_data["fields"].get("Employer Name", ""))
selected_option = select.first_selected_option
print(f"Selected Employment Status: {selected_option.text}")

# 'Occupation' 입력 필드 찾기
# Occupation 
occupation_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtOccupationCurEmp")

# 값 입력
# occupation_value = "Software Engineer"
# occupation_input.send_keys(occupation_value)
occupation_input.send_keys(_data["fields"].get("Occupation", ""))


# 입력된 값 확인
entered_value = occupation_input.get_attribute("value")
print(f"Entered Occupation: {entered_value}")  # 출력: Entered Occupation: Software Engineer

# 'Duration Current Employer Address' 입력 필드 찾기
# Duration of Employment
duration_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_Y")

# 값 설정 (예: "12" - 2자리 숫자)
# duration_value = "2"
# duration_input.send_keys(duration_value)

# 입력된 값 확인
duration_input.send_keys(_data["fields"].get("Duration of Employment", ""))
entered_value = duration_input.get_attribute("value")
print(f"Entered Duration: {entered_value}")  # 출력: Entered Duration: 12

# 'Duration Current Employer Address - Month' 입력 필드 찾기
month_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_M")

# 값 설정 (예: "06" - 2자리 숫자)
month_value = "6"
month_input.send_keys(month_value)

# 입력된 값 확인
entered_value = month_input.get_attribute("value")
print(f"Entered Month Duration: {entered_value}")  # 출력: Entered Month Duration: 06

# 'Address Type Current Employer' 드롭다운 찾기
address_type_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlAddressTypeCurEmp")

# Select 객체로 드롭다운을 제어
select = Select(address_type_dropdown)

# "Street" 옵션 선택 (value="ST")
# ST : Street
# RR : Rural Route
# PB : Postal Box
select.select_by_value("ST")

selected_option = select.first_selected_option
print(f"Selected Address Type: {selected_option.text}")

# 'Suite Number Current Employer' 입력 필드 찾기
suite_number_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtSuiteNumberCurEmp")

suite_number_input.send_keys("123A")

entered_value = suite_number_input.get_attribute("value")
print(f"Entered Suite Number: {entered_value}")  # 출력: Entered Suite Number: 123A

# 'Street Number Current Employer' 입력 필드 찾기
street_number_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtStreetNumberCurEmp")
street_number_input.send_keys("456")
entered_value = street_number_input.get_attribute("value")
print(f"Entered Street Number: {entered_value}")  # 출력: Entered Street Number: 456


# 'Street Name Current Employer' 입력 필드 찾기
street_name_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtStreetNameCurEmp")
street_name_input.send_keys("Maple Street")
entered_value = street_name_input.get_attribute("value")
print(f"Entered Street Name: {entered_value}")  # 출력: Entered Street Name: Maple Street



# 'Street Type Current Employer' 드롭다운 메뉴 찾기
street_type_select = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlStreetTypeCurEmp")

# 드롭다운 메뉴로 옵션 선택하기
# AB : ABBEY
# AS : ACRES
# AE : ALLEE
# AL : ALLEY
# AU : AUTOROUTE
# AV : AVENUE
# BA : BAY
# BE : BEACH
# BN : BEND
# BV : BLVD
# BO : BOUL
# BP : BYPASS
# CA : CAMPUS
# CP : CAPE
# CR : CARRE
# CN : CENTRE
# CC : CERCLE
# CE : CHASE
# CH : CHEMIN
# CI : CIRCLE
# CF : CIRCUIT
# CL : CLOSE
# CM : COMMON
# CQ : CONCESSION
# CB : COMRNERS
# CO : COTE
# CU : COUR
# CY : COURS
# CT : COURT
# CV : COVE
# CS : CRESENT
# CW : CROISSANT
# CD : CUL-DE-SAC
# DA : DALE
# DE : DELL
# DI : DIVERSION
# EN : END
# EP : ESPLANADE
# ES : ESTATES
# EX : EXPRESSWAY
# ET : EXTENSION
# FI : FIELD
# FY : FREEWAY
# FR : FRONT
# GD : GARDENS
# GT : GATE
# GL : GLADE
# GE : GLEN
# GN : 

# value="ST": 텍스트 "STREET"
# value="RR": 텍스트 "Rural Route"
# value="PB": 텍스트 "Postal Box"
# value="AV": 텍스트 "AVENUE"
# value="BA": 텍스트 "BAY"
# value="BE": 텍스트 "BEACH"
# value="BN": 텍스트 "BEND"
# value="BV": 텍스트 "BLVD"
# value="BO": 텍스트 "BOUL"
# value="BP": 텍스트 "BYPASS"
# value="CA": 텍스트 "CAMPUS"
# value="CP": 텍스트 "CAPE"
# value="CR": 텍스트 "CARRE"
# value="CN": 텍스트 "CENTRE"
# value="CC": 텍스트 "CERCLE"
# value="CE": 텍스트 "CHASE"
# value="CH": 텍스트 "CHEMIN"
# value="CI": 텍스트 "CIRCLE"
# value="CF": 텍스트 "CIRCUIT"
# value="CL": 텍스트 "CLOSE"
# value="CM": 텍스트 "COMMON"
# value="CQ": 텍스트 "CONCESSION"
# value="CB": 텍스트 "CORNERS"
# value="CO": 텍스트 "COTE"
# value="CU": 텍스트 "COUR"
# value="CY": 텍스트 "COURS"
# value="CT": 텍스트 "COURT"
# value="CV": 텍스트 "COVE"
# value="CS": 텍스트 "CRESCENT"
# value="CW": 텍스트 "CROISSANT"
# value="CX": 텍스트 "CROSSING"
# value="CD": 텍스트 "CUL-DE-SAC"
# value="DA": 텍스트 "DALE"
# value="DE": 텍스트 "DELL"
# value="DI": 텍스트 "DIVERSION"
# value="DO": 텍스트 "DOWNS"
# value="DR": 텍스트 "DRIVE"
# value="EN": 텍스트 "END"
# value="EP": 텍스트 "ESPLANADE"
# value="ES": 텍스트 "ESTATES"
# value="EX": 텍스트 "EXPRESSWAY"
# value="ET": 텍스트 "EXTENSION"
# value="FI": 텍스트 "FIELD"
# value="FY": 텍스트 "FREEWAY"
# value="FR": 텍스트 "FRONT"
# value="GD": 텍스트 "GARDENS"
# value="GT": 텍스트 "GATE"
# value="GL": 텍스트 "GLADE"
# value="GE": 텍스트 "GLEN"
# value="GN": 텍스트 "GREEN"
# value="GA": 텍스트 "GROUNDS"
# value="GR": 텍스트 "GROVE"
# value="HA": 텍스트 "HARBOUR"
# value="HE": 텍스트 "HEATH"
# value="HT": 텍스트 "HEIGHTS"
# value="HG": 텍스트 "HIGHLANDS"
# value="HW": 텍스트 "HIGHWAY"
# value="HL": 텍스트 "HILL"
# value="HO": 텍스트 "HOLLOW"
# value="IL": 텍스트 "ILE"
# value="IM": 텍스트 "IMPASSE"
# value="IN": 텍스트 "INLET"
# value="IS": 텍스트 "ISLAND"
# value="KE": 텍스트 "KEY"
# value="KN": 텍스트 "KNOLL"
# value="LA": 텍스트 "LANDNG"
# value="LN": 텍스트 "LANE"
# value="LM": 텍스트 "LIMITS"
# value="LE": 텍스트 "LINE"
# value="LI": 텍스트 "LINK"
# value="LK": 텍스트 "LOOKOUT"
# value="LP": 텍스트 "LOOP"
# value="MA": 텍스트 "MALL"
# value="MR": 텍스트 "MANOR"
# value="MZ": 텍스트 "MAZE"
# value="MW": 텍스트 "MEADOW"
# value="MS": 텍스트 "MEWS"
# value="MN": 텍스트 "MONTEE"
# value="MO": 텍스트 "MOUNT"
# value="MT": 텍스트 "MOUNTAIN"
# value="PR": 텍스트 "PARADE"
# value="PC": 텍스트 "PARC"
# value="PK": 텍스트 "PARK"
# value="PY": 텍스트 "PARKWAY"
# value="PS": 텍스트 "PASSAGE"
# value="PA": 텍스트 "PATH"
# value="PW": 텍스트 "PATHWAY"
# value="PL": 텍스트 "PLACE"
# value="PP": 텍스트 "PLATEAU"
# value="PZ": 텍스트 "PLAZA"
# value="PQ": 텍스트 "POINT"
# value="PT": 텍스트 "POINTE"
# value="PV": 텍스트 "PRIVATE"
# value="PE": 텍스트 "PROMENADE"
# value="QU": 텍스트 "QUAI"
# value="QY": 텍스트 "QUAY"
# value="RM": 텍스트 "RAMP"
# value="RA": 텍스트 "RANG"
# value="RG": 텍스트 "RANGE"
# value="RE": 텍스트 "RIDGE"
# value="RI": 텍스트 "RISE"
# value="RD": 텍스트 "ROAD"
# value="RT": 텍스트 "ROUTE"
# value="RO": 텍스트 "ROW"
# value="RU": 텍스트 "RUE"
# value="RL": 텍스트 "RUELLE"
# value="RN": 텍스트 "RUN"
# value="SN": 텍스트 "SENTIER"
# value="SQ": 텍스트 "SQUARE"
# value="SU": 텍스트 "SUBDIVISION"
# value="TC": 텍스트 "TERRACE"
# value="TS": 텍스트 "TERRASSE"
# value="TL": 텍스트 "TOWNLINE"
# value="TR": 텍스트 "TRAIL"
# value="TT": 텍스트 "TURNABOUT"
# value="VL": 텍스트 "VALE"
# value="VW": 텍스트 "VIEW"
# value="VI": 텍스트 "VILLAGE"
# value="VA": 텍스트 "VILLAS"
# value="VS": 텍스트 "VISTA"
# value="VO": 텍스트 "VOIE"
# value="WK": 텍스트 "WALK"
# value="WY": 텍스트 "WAY"
# value="WH": 텍스트 "WHARF"
# value="WO": 텍스트 "WOOD"
# value="WN": 텍스트 "WYND"
select = Select(street_type_select)
select.select_by_value("AV")  # 예: "AVENUE"를 선택하려면 "AV" 값을 사용

# 선택된 옵션 확인
selected_option = select.first_selected_option
print(f"Selected Street Type: {selected_option.text}")  # 출력: Selected Street Type: AVENUE


# 'Direction' 드롭다운 요소 찾기
direction_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlDirectionCurEmp")

# Select 객체 생성
select = Select(direction_dropdown)

# 값 선택 (예: 'North')
# value="E": 텍스트 "East"
# value="N": 텍스트 "North"
# value="NE": 텍스트 "North East"
# value="NW": 텍스트 "North West"
# value="S": 텍스트 "South"
# value="SE": 텍스트 "South East"
# value="SW": 텍스트 "South West"
# value="W": 텍스트 "West"
direction_value = "N"
select.select_by_value(direction_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Direction: {selected_option.text}")  # 출력: Selected Direction: North

# 'City' 텍스트 입력 필드 찾기
# Employer City
city_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00__txtCityCurEmp")
city_input.clear()
# 값 입력 (예: 'Toronto')
# city_input.send_keys("Toronto")
city_input.send_keys(_data["fields"].get("Employer City", ""))

# 입력된 값 확인
print(f"Entered City: {city_input.get_attribute('value')}")  # 출력: Entered City: Toronto

# 'Province' 드롭다운 요소 찾기
# Employer Province
province_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00__ddlProvinceCurEmp")

# Select 객체 생성
select = Select(province_dropdown)

# 값 선택 (예: 'Ontario')
# value=1 : Alberta
# value=2 : British Columbia
# value=3 : Manitoba
# value=4 : New Brunswick
# value=5 : Newfoundland
# value=6 : Northwest Territories
# value=7 : Nova Scotia
# value=8 : Nunavut
# value=9 : Ontario
# value=10 : Prince Edward Island
# value=11 : Quebec
# value=12 : Saskatchewan
# value=13 : Yukon

# province_value = "9"
# select.select_by_value(province_value)
select.select_by_visible_text(_data["fields"].get("Employer Province", ""))
# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Province: {selected_option.text}")  # 출력: Selected Province: Ontario

# 'Postal Code' 입력 필드 찾기
# Employer Postal Code
postal_code_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtPostalCodeCurEmp")
postal_code_input.click()
postal_code_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

# 값 입력 (예: 'M1A 2B3')
# postal_code_value = "M1A2B3"
postal_code_input.send_keys(_data["fields"].get("Employer Postal Code", ""))

# 입력된 값 확인
print(f"Entered Postal Code: {postal_code_input.get_attribute('value')}")  # 출력: Entered Postal Code: M1A 2B3

# 'Telephone' 입력 필드 찾기
# Employer Phone
telephone_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtTelephoneCurEmp")
# telephone_input.click()
# telephone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 값 입력 (예: '123-456-7890')
# telephone_value = "4374536013"
# phone_number = "4374536013"  # 예시 전화번호
if "Employer Phone" in _data["fields"]:
    phone_number = remove_country_code_and_non_digits(_data["fields"]["Employer Phone"])
telephone_input.send_keys(phone_number)

# 입력된 값 확인
print(f"Entered Telephone: {telephone_input.get_attribute('value')}")  # 출력: Entered Telephone: 123-456-7890

time.sleep(1)
# 'Extension' 입력 필드 찾기
# extension_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtExtensionCurEmp")
# extension_input.click()
# extension_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 값 입력 (예: '12345')
# extension_value = "12345"
# extension_input.send_keys(extension_value)

# 입력된 값 확인
# print(f"Entered Extension: {extension_input.get_attribute('value')}")  # 출력: Entered Extension: 12345

######################################################## Previous Employment ##############################################################
###########################################################################################################################################
# Duration < 2 면 작성

######################################################## Income Details ###################################################################
###########################################################################################################################################

# 'Gross Income' 입력 필드 찾기
gross_income_input = driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtGrossIncome")
# 값 입력 (예: '50000')
gross_income_value = "50000"
gross_income_input.clear()
gross_income_input.send_keys(gross_income_value)

# 입력된 값 확인
print(f"Entered Gross Income: {gross_income_input.get_attribute('value')}")  # 출력: Entered Gross Income: 50000

# 'Income Basis' 드롭다운 요소 찾기
income_basis_dropdown = driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlIncomeBasis")
income_basis_dropdown.click()
# Select 객체 생성
select = Select(income_basis_dropdown)

# 값 선택 (예: 'Month')
# value=1 : Year
# value=12 : Month
# value=52 : Week
income_basis_value = "12"
select.select_by_value(income_basis_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Income Basis: {selected_option.text}")  # 출력: Selected Income Basis: Month


# 'Other Income Type' 드롭다운 요소 찾기
other_income_type_dropdown = driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlOtherIncomeType")

# Select 객체 생성
select = Select(other_income_type_dropdown)

# 값 선택 (예: 'Disability Payments')
# value="Car Allowance" : Car Allowance
# value="Child Support/Alimony" : Child Support/Alimony
# value="Disability Payments" : Disability Payments
# value="Investment Income" : Investment Income
# value="Other" : Other
# value="Pensions" : Pensions
# value="Rental Income" : Rental Income
# value="Workers Compensation" : Workers Compensation
other_income_type_value = "Disability Payments"
select.select_by_visible_text(other_income_type_value)

selected_option = select.first_selected_option
print(f"Selected Other Income Type: {selected_option.text}")  # 출력: Selected Other Income Type: Disability Payments

# 10초간 기다리기
# 'Other Income' 입력 필드 찾기
other_income_input = driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtOtherIncome")

# 값 입력 (예: '1000')
other_income_value = "1000"
other_income_input.clear()
other_income_input.send_keys(other_income_value)

# 입력된 값 확인
entered_value = other_income_input.get_attribute("value")

print(f"Entered Other Income: {entered_value}")  # 출력: Entered Other Income: 1000


# 'Other Income Basis' 드롭다운 요소 찾기
other_income_basis_dropdown = driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlOtherIncomeBasis")

# Select 객체 생성
select = Select(other_income_basis_dropdown)

# 값 선택 (예: 'Month')
# value=1 : Year
# value=12 : Month
# value=52 : Week
other_income_basis_value = "12"
select.select_by_value(other_income_basis_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Other Income Basis: {selected_option.text}")  # 출력: Selected Other Income Basis: Month

if other_income_type_value=="Other":
    # 'Other Description' 텍스트 필드 요소 찾기
    other_description_input = driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtOtherDescription")

    # 값 입력 (예: 'Additional Income')
    other_description_value = "Additional Income"
    other_description_input.send_keys(other_description_value)

    # 입력된 값 확인
    entered_value = other_description_input.get_attribute("value")
    print(f"Entered Other Description: {entered_value}")

######################################################## Financial Summary ################################################################
###########################################################################################################################################

##################################################### Assets and Liabilities ##############################################################
###########################################################################################################################################


###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

################################################################ Worksheet ################################################################
###########################################################################################################################################
###########################################################################################################################################
# 'Worksheet' 링크 요소 찾기
worksheet_link = driver.find_element(By.ID, "ctl21_btnWORKSHEET")

# 링크 클릭
worksheet_link.click()

########################################################### Vehicle Selection #############################################################
###########################################################################################################################################

# 'VIN' 입력 필드 찾기
# 'VIN' 입력 필드 로드될 때까지 기다리기 (최대 20초)
try:
    vin_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl19_ctl00_txtVIN"))
    )
    print("VIN input field is loaded.")
except:
    print("Timeout: VIN input field was not found.")

# 값 입력 (예: '1HGCM82633A123456')
# vin_value = "1HGCM82633A123456"
# vin_input.send_keys(vin_value)
vin_input.send_keys(_data["fields"].get("VIN", ""))


# 입력된 값 확인
entered_value = vin_input.get_attribute("value")
print(f"Entered VIN: {entered_value}")  # 출력: Entered VIN: 1HGCM82633A123456

# 'VIN Lookup' 버튼 찾기
vin_lookup_button = driver.find_element(By.ID, "ctl21_ctl19_ctl00_btnVINLookup")

# 버튼 클릭
vin_lookup_button.click()

# 'VIN Lookup' 제목이 나타날 때까지 대기
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "DTC$ModalPopup$TitleID3"))
)

# 데이터를 JSON 파일로 저장
# with open("source.txt", 'w', encoding='utf-8') as f:
#     json.dump(driver.page_source, f, ensure_ascii=False, indent=4)

# iframe로 전환 (VIN Lookup 창이 iframe에 포함되어 있으므로)
iframe = driver.find_element(By.ID, "DTC$ModalPopup$Frame")
driver.switch_to.frame(iframe)

# 테이블을 찾고, 모든 행을 가져오기
try:
    table = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "gvVehicles"))
    )
    print("table field is loaded.")
except:
    print("Timeout: table field was not found.")

rows = table.find_elements(By.TAG_NAME, "tr")

# 'Series' 열에 있는 값을 비교할 값 설정
# "Vehicle Trim"
if "Vehicle Trim" in _data["fields"]:
    target_series = str(_data["fields"].get("Vehicle Trim", ""))

    # 첫 번째 행은 헤더이므로 두 번째 행부터 시작
    for row in rows[1:]:
        # 각 행의 모든 셀(td 요소)을 가져오기
        cells = row.find_elements(By.TAG_NAME, "td")

        # 셀이 충분히 있는지 확인 (Series 열은 6번째, 인덱스는 5)
        if len(cells) > 5:
            # 'Series' 열의 값을 가져오기 (6번째 열)
            series_value = cells[5].text.strip()

            # 'Series' 값이 target_series와 일치하는지 비교
            if series_value == target_series.capitalize() or \
               series_value == target_series.upper() or \
               series_value == target_series.lower():
                # 해당 행의 라디오 버튼을 클릭 (라디오 버튼은 2번째 열에 있음)
                radio_button = cells[1].find_element(By.TAG_NAME, "input")
                radio_button.click()
                break  # 일치하는 값을 찾으면 클릭하고 반복 종료
    else:
        # 일치하는 값이 없을 경우 첫 번째 라디오 버튼 클릭
        first_row = rows[1]
        first_radio_button = first_row.find_elements(By.TAG_NAME, "td")[1].find_element(By.TAG_NAME, "input")
        first_radio_button.click()

# print(f"일치하는 값: {matching_value}")


# 'Close' 버튼 클릭
# try:
#     # Close 버튼을 클릭하여 창을 닫음
#     # close_button = driver.find_element(By.ID, "DTC$ModalPopup$CloseImg")
#     # close_button.click()
#     close_button = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "DTC$ModalPopup$CloseImg"))
#     )
#     close_button.click()
#     # ActionChains(driver).move_to_element(close_button).click().perform()
#     print("close_button btn is loaded.")
# except:
#     print("Timeout: close_button btn was not found.")


# 버튼이 로드될 때까지 대기
wait = WebDriverWait(driver, 10)
btnOK = wait.until(EC.element_to_be_clickable((By.ID, "btnOK")))

# 버튼 클릭
btnOK.click()
print("Submit 성공")

# iframe 밖으로 이동
driver.switch_to.parent_frame()
# driver.switch_to.default_content() 는 에러가 발생했음

# 마일리지 값 입력
# wait.until(EC.presence_of_element_located((By.ID, "ctl21_ctl19_ctl00_txtCurrentKMs")))
txtCurrentKMs_field = wait.until(EC.presence_of_element_located((By.ID, "ctl21_ctl19_ctl00_txtCurrentKMs")))
# 텍스트 필드에 JSON 데이터 값 입력
txtCurrentKMs_field.clear()  # 기존 값 제거
txtCurrentKMs_field.send_keys(_data["fields"].get("Odometer", ""))
print(f"txtCurrentKMs_field: {txtCurrentKMs_field}")

######################################################### VIN ##############################################################
# 'Stock Number' 입력 필드 찾기
# stock_number_input = driver.find_element(By.ID, "ctl21_ctl19_ctl00_txtStockNumber")

# # 값 입력 (예: 'STK12345')
# stock_number_value = "STK12345"
# stock_number_input.send_keys(stock_number_value)

# # 입력된 값 확인
# entered_value = stock_number_input.get_attribute("value")
# print(f"Entered Stock Number: {entered_value}")  # 출력: Entered Stock Number: STK12345

# # 'Residual Month' 드롭다운 요소 찾기
# residual_month_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlResidualMonth")

# # Select 객체 생성
# select = Select(residual_month_dropdown)

# # 값 선택 (예: '202411')
# # value="202412"
# # value="202411"
# residual_month_value = "202411"
# select.select_by_value(residual_month_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Residual Month: {selected_option.text}")  # 출력: Selected Residual Month: November, 2024


# # 'Vehicle Condition' 드롭다운 요소 찾기
# vehicle_condition_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleCondition")
# time.sleep(1)


# # Select 객체 생성
# select = Select(vehicle_condition_dropdown)

# # 값 선택 (예: 'U' for Used)
# # value="N" : New
# # value="U" : Used
# vehicle_condition_value = "U"
# select.select_by_value(vehicle_condition_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Condition: {selected_option.text}")  # 출력: Selected Vehicle Condition: Used

# # 'Vehicle Year' 드롭다운 요소 찾기
# vehicle_year_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleYear")
# time.sleep(1)

# # Select 객체 생성
# select = Select(vehicle_year_dropdown)

# # 값 선택 (예: '2024')
# vehicle_year_value = "2024"
# select.select_by_value(vehicle_year_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Year: {selected_option.text}")  # 출력: Selected Vehicle Year: 2024

# # 'Vehicle Make' 드롭다운 요소 찾기
# vehicle_make_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleMake")
# time.sleep(1)

# # Select 객체 생성
# select = Select(vehicle_make_dropdown)

# # 값 선택 (예: 'Honda')
# # <option value="">Select an option</option>
# # <option value="AC">Acura</option>
# # <option value="AR">Alfa Romeo</option>
# # <option value="AU">Audi</option>
# # <option value="BM">BMW</option>
# # <option value="BU">Buick</option>
# # <option value="CA">Cadillac</option>
# # <option value="CV">Chevrolet</option>
# # <option value="CH">Chrysler</option>
# # <option value="DW">Daewoo</option>
# # <option value="DO">Dodge</option>
# # <option value="FI">Fiat</option>
# # <option value="FK">Fisker</option>
# # <option value="FO">Ford</option>
# # <option value="GN">Genesis</option>
# # <option value="GM">GMC</option>
# # <option value="HO">Honda</option>
# # <option value="HU">Hummer</option>
# # <option value="HY">Hyundai</option>
# # <option value="IE">Ineos</option>
# # <option value="IN">Infiniti</option>
# # <option value="IS">Isuzu</option>
# # <option value="JG">Jaguar</option>
# # <option value="JE">Jeep</option>
# # <option value="KI">Kia</option>
# # <option value="LR">Land Rover</option>
# # <option value="LE">Lexus</option>
# # <option value="LI">Lincoln</option>
# # <option value="LU">Lucid</option>
# # <option value="MS">Maserati</option>
# # <option value="MA">Mazda</option>
# # <option value="ME">Mercedes-Benz</option>
# # <option value="MY">Mercury</option>
# # <option value="MN">Mini</option>
# # <option value="MI">Mitsubishi</option>
# # <option value="NI">Nissan</option>
# # <option value="OL">Oldsmobile</option>
# # <option value="PL">Plymouth</option>
# # <option value="PS">Polestar</option>
# # <option value="PO">Pontiac</option>
# # <option value="PR">Porsche</option>
# # <option value="RA">Ram</option>
# # <option value="RI">Rivian</option>
# # <option value="SB">Saab</option>
# # <option value="SA">Saturn</option>
# # <option value="SC">Scion</option>
# # <option value="SM">Smart</option>
# # <option value="SU">Subaru</option>
# # <option value="SZ">Suzuki</option>
# # <option value="TE">Tesla</option>
# # <option value="TO">Toyota</option>
# # <option value="VF">Vinfast</option>
# # <option value="VW">Volkswagen</option>
# # <option value="VO">Volvo</option>

# vehicle_make_value = "VO"
# select.select_by_value(vehicle_make_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Make: {selected_option.text}")  # 출력: Selected Vehicle Make: Honda


# # "Vehicle Model"
# # 'Vehicle Model' 드롭다운 요소 찾기
# vehicle_model_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleModel")
# time.sleep(1)

# # Select 객체 생성
# select = Select(vehicle_model_dropdown)

# # 값 선택 (예: 'MDX')
# vehicle_model_value = "C40"
# select.select_by_value(vehicle_model_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Model: {selected_option.text}")  # 출력: Selected Vehicle Model: MDX

# # 'Vehicle Series' 드롭다운 요소 찾기
# vehicle_series_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleSeries")
# time.sleep(1)

# # Select 객체 생성
# select = Select(vehicle_series_dropdown)

# # 값 선택 (예: 'Recharge Plus')
# vehicle_series_value = "Recharge Plus"
# select.select_by_value(vehicle_series_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Series: {selected_option.text}")  # 출력: Selected Vehicle Series: Recharge Plus

# # 'Vehicle Body Style' 드롭다운 요소 찾기
# vehicle_body_style_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleBodyStyle")
# time.sleep(1)

# # Select 객체 생성
# select = Select(vehicle_body_style_dropdown)

# # 값 선택 (예: '4D Utility')
# vehicle_body_style_value = "4D Utility"
# select.select_by_value(vehicle_body_style_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Body Style: {selected_option.text}")  # 출력: Selected Vehicle Body Style: 4D Utility

# # 'Vehicle Includes' 드롭다운 요소 찾기
# vehicle_includes_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleIncludes")
# time.sleep(1)

# # Select 객체 생성
# select = Select(vehicle_includes_dropdown)

# # 값 선택 (예: 'AC AT CC ES')
# vehicle_includes_value = "AC AT CC ES"
# select.select_by_value(vehicle_includes_value)

# # 선택된 값 확인
# selected_option = select.first_selected_option
# print(f"Selected Vehicle Includes: {selected_option.text}")  # 출력: Selected Vehicle Includes: AC AT CC ES
###########################################################################################################################################

########################################################### Program Selection #############################################################
###########################################################################################################################################

# Loan Term * 12 = Term
# Term = Amortization
# Car Price 입력후 interest rate check
# 'program_selection' 드롭다운 요소 찾기
program_selection_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl21_ctl00_ddlProgram")))
time.sleep(1)

# Select 객체 생성
select = Select(program_selection_dropdown)

# 값 선택 (예: 'AC AT CC ES')
# 1966420 = Auto special
# 1966448 = standard fixed rate
program_selection_value = "1966420"
select.select_by_value(program_selection_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Program: {selected_option.text}")

############################################################ Purchase Details #############################################################
###########################################################################################################################################
# 'Cash Price' 입력 필드 찾기
# wait.until(EC.presence_of_element_located((By.ID, "ctl21_ctl23_ctl00_txtCashPrice")))
cash_price_input = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl23_ctl00_txtCashPrice")))

# 값 입력하기
cash_price_input.click()
time.sleep(0.5)

cash_price_input.send_keys(str(_data["fields"].get("Cash Price", "")))
cash_price_input.send_keys(Keys.TAB)

# 입력된 값 확인
entered_value = cash_price_input.get_attribute("value")
print(f"Entered Cash Price: {entered_value}")  
######################################################### Financing Terms #################################################################
###########################################################################################################################################
# Loan Term
# 'Term' 드롭다운 필드 찾기
term_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlTerm")

# 드롭다운 선택을 위한 Select 객체 생성
select_term = Select(term_dropdown)

# 값을 선택 (예: '24')
term_value = remove_country_code_and_non_digits(_data["fields"].get("Loan Term", 0))
term_value = int(term_value) * 12
select_term.select_by_value(str(term_value))

time.sleep(1)
selected_option = select_term.first_selected_option
print(f"Selected Term: {selected_option.text}")


# 'Amortization' 드롭다운 필드 찾기
amortization_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlAmortization")

# 드롭다운 선택을 위한 Select 객체 생성
select_amortization = Select(amortization_dropdown)
select_amortization.select_by_value(str(term_value))

time.sleep(1)

selected_option = select_amortization.first_selected_option
print(f"Selected Amortization: {selected_option.text}")  # 출력: Selected Amortization: 36

# 'Payment Frequency' 드롭다운 필드 찾기
# Payment Frequency

payment_frequency_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlPaymentFrequency")

# 드롭다운 선택을 위한 Select 객체 생성
select_payment_frequency = Select(payment_frequency_dropdown)

if "Payment Frequency" in _data["fields"]:
    if _data["fields"]["Payment Frequency"]=="Monthly":
        payment_frequency_value = "12"
    elif _data["fields"]["Payment Frequency"]=="Bi-Weekly":
        payment_frequency_value = "26"
    elif _data["fields"]["Payment Frequency"]=="Weekly":
        payment_frequency_value = "52"

select_payment_frequency.select_by_value(payment_frequency_value)

# 선택된 값 확인
selected_option = select_payment_frequency.first_selected_option
print(f"Selected Payment Frequency: {selected_option.text}")

time.sleep(1)
# # 'Dealer Interest Rate' 입력 필드 찾기
# dealer_interest_rate_input = driver.find_element(By.ID, "ctl21_ctl32_ctl00_txtDealerInterestRate")

# # 값 입력 (예: '5.5')
# dealer_interest_rate_value = "5.5"
# dealer_interest_rate_input.clear()  # 기존 값 지우기
# dealer_interest_rate_input.send_keys(dealer_interest_rate_value)

# # 입력된 값 확인
# entered_value = dealer_interest_rate_input.get_attribute("value")
# print(f"Entered Dealer Interest Rate: {entered_value}")  # 출력: Entered Dealer Interest Rate: 5.5

wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl23_ctl00_txtCashPrice")))
# interest rate
while True:
    select_element = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl32_ctl00_ddlInterestRate")))
    options = select_element.find_elements(By.TAG_NAME, 'option')

    # 옵션이 없으면 다른 작업을 수행
    if not options:
        print("옵션 값이 없습니다. 다른 작업을 수행합니다.")

        # 'program_selection' 드롭다운 요소 찾기
        program_selection_dropdown = driver.find_element(By.ID, "ctl21_ctl21_ctl00_ddlProgram")
        time.sleep(1)

        if program_selection_value == "1966448":
            term_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlTerm")

            # 드롭다운 선택을 위한 Select 객체 생성
            select_term = Select(term_dropdown)

            # 값을 선택 (예: '24')
            term_value = remove_country_code_and_non_digits(_data["fields"].get("Loan Term", 0))
            term_value = int(term_value) * 12 - 12
            select_term.select_by_value(str(term_value))

            time.sleep(1)
            selected_option = select_term.first_selected_option
            print(f"Selected Term: {selected_option.text}")


            # 'Amortization' 드롭다운 필드 찾기
            amortization_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlAmortization")

            # 드롭다운 선택을 위한 Select 객체 생성
            select_amortization = Select(amortization_dropdown)
            select_amortization.select_by_value(str(term_value))

            time.sleep(1)

            selected_option = select_amortization.first_selected_option
            print(f"Selected Amortization: {selected_option.text}")  # 출력: Selected Amortization: 36

        # Select 객체 생성
        select = Select(program_selection_dropdown)

        # 값 선택 (예: 'AC AT CC ES')
        # 1966420 = Auto special
        # 1966448 = standard fixed rate
        program_selection_value = "1966448"
        select.select_by_value(program_selection_value)

        # 선택된 값 확인
        selected_option = select.first_selected_option
        print(f"Selected Program: {selected_option.text}")  
        # 여기에 다른 작업을 수행할 수 있는 코드를 추가하세요
    else:
        # 가장 큰 값을 찾기
        max_value = max([float(option.get_attribute('value')) for option in options])
        print(f"가장 큰 옵션 값: {max_value}")

        # 가장 큰 값을 가진 옵션을 선택
        select = Select(select_element)
        select.select_by_value(str(max_value))
        print(f"옵션 {max_value} 선택됨")
        break


############################################### Additional Lender Information #############################################################
###########################################################################################################################################

scene_card_input = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl20_ctl00_txtSceneCard")))
scene_card_input.send_keys("5718683723")

entered_value = scene_card_input.get_attribute("value")
print(f"Entered Scene Card: {entered_value}")

# # 'Sales Code' 입력 필드 찾기
# sales_code_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtSalesCode")

# # 값 입력 (예: 'ABC123')
# sales_code_value = "ABC123"
# sales_code_input.clear()  # 기존 값 지우기
# sales_code_input.send_keys(sales_code_value)

# # 입력된 값 확인
# entered_value = sales_code_input.get_attribute("value")
# print(f"Entered Sales Code: {entered_value}")  # 출력: Entered Sales Code: ABC123



#################################################### Special Discount Program #############################################################
###########################################################################################################################################


#################################################################### Trade In #############################################################
###########################################################################################################################################
if "Trade In" in _data["fields"]:
    if _data["fields"].get("Trade In", "")=="Yes":

        # Trade-In Year
        year_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtYear")
        year_input.clear()
        year_input.send_keys(_data["fields"].get("Trade-In Year", ""))  # 새로운 값 입력

        entered_value = year_input.get_attribute("value")
        print(f"Entered Cash Down Payment: {entered_value}")

        # Trade-In Make
        make_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtMake")
        make_input.clear()
        make_input.send_keys(_data["fields"].get("Trade-In Make", ""))
        entered_value = make_input.get_attribute("value")
        print(f"Entered Cash Down Payment: {entered_value}")

        # Trade-In Model
        model_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtModel")
        model_input.clear()
        model_input.send_keys(_data["fields"].get("Trade-In Model", ""))
        entered_value = model_input.get_attribute("value")
        print(f"Entered Cash Down Payment: {entered_value}")

        # Trade-In VIN
        vin_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtVIN")
        vin_input.clear()
        vin_input.send_keys(_data["fields"].get("Trade-In VIN", ""))
        entered_value = vin_input.get_attribute("value")
        print(f"Entered Cash Down Payment: {entered_value}")

        # Trade-In Odometer
        mileage_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtMileage")
        mileage_input.clear()
        mileage_input.send_keys(_data["fields"].get("Trade-In Odometer", ""))
        entered_value = mileage_input.get_attribute("value")
        print(f"Entered Cash Down Payment: {entered_value}")
        
        # Allowance
        allowance_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtAllowance")
        allowance_input.clear()
        allowance_input.send_keys(_data["fields"].get("Allowance", ""))
        entered_value = allowance_input.get_attribute("value")
        print(f"Entered Cash Down Payment: {entered_value}")


#################################################################### Lien #################################################################
###########################################################################################################################################
# 'Lien Amount' 입력 필드 찾기
if "Trade-In Lien" in _data["fields"]:
    if _data["fields"].get("Trade-In Lien", "")=="Yes":
        lien_amount_input = driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtLienAmount")
        lien_amount_input.clear()
        lien_amount_input.send_keys(_data["fields"].get("Trade-In Lien", ""))
        entered_value = lien_amount_input.get_attribute("value")
        print(f"Entered Lien Amount: {entered_value}")

        # balance_owe_to
        # Trade-In Lender
        balance_owe_to_input = driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtBalanceOwedTo")
        balance_owe_to_input.clear()
        balance_owe_to_input.send_keys(_data["fields"].get("Trade-In Lender", ""))
        entered_value = balance_owe_to_input.get_attribute("value")
        print(f"Entered Lien Amount: {entered_value}")

################################################################### Taxes #################################################################
###########################################################################################################################################
# 'Province' 드롭다운 필드 찾기
# province_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlProvince")

# # '9' -> Ontario)
# province_value = "9"
# select = Select(province_dropdown)
# select.select_by_value(province_value)

# # 'PST' 드롭다운 필드 찾기
# pst_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlPST")

# # 'GSTHST' 드롭다운 필드 찾기
# gst_hst_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlGSTHST")

# if pst_value=="0":
#     # 'PSTExemption' 드롭다운 필드 찾기
#     pst_exemption_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlPSTExemption")

# if gst_hst_value=="0":
#     # 'GSTExemption' 드롭다운 필드 찾기
#     gst_exemption_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlGSTExemption")
#################################################################### Fees #################################################################
###########################################################################################################################################
# 'CashDownPayment' 입력 필드 찾기
# Cash Down Payment
if "Cash Down Payment" in _data["fields"]:
    cash_down_payment_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtCashDownPayment")
    cash_down_payment_input.clear()
    cash_down_payment_input.send_keys(_data["fields"].get("Cash Down Payment", ""))

    entered_value = cash_down_payment_input.get_attribute("value")
    print(f"Entered Cash Down Payment: {entered_value}")

# 'Other Taxable' 입력 필드 찾기
# "Other Taxable Amounts"
if "Other Taxable Amounts" in _data["fields"]:
    if "Theft Protection" in _data["fields"]:
        if _data["fields"].get("Theft Protection", "")=="Yes":
            # Theft Protection Amount
            if int(_data["fields"].get("Theft Protection Amount", ""))>=99 or int(_data["fields"].get("Theft Protection Amount", ""))<=250:
                theft_protection_amount = int(_data["fields"].get("Theft Protection Amount", ""))
                print(f"theft_protection_amount: {theft_protection_amount}")

                other_taxable_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxable")
                other_taxable_input.clear()

                other_taxable_amount = int(_data["fields"].get("Other Taxable Amounts", "")) + theft_protection_amount

                other_taxable_input.send_keys(other_taxable_amount)
                entered_value = other_taxable_input.get_attribute("value")
                print(f"Entered Other Taxable: {entered_value}")

                other_taxable_desc_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxableDesc")
                other_taxable_desc_input.clear()
                other_taxable_desc_input.send_keys("ADMIN/OMVIC/THEFT PROTECTION")
                entered_value = other_taxable_desc_input.get_attribute("value")
                print(f"Entered Other Taxable Description: {entered_value}")

        else:
            other_taxable_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxable")
            other_taxable_input.clear()
            other_taxable_input.send_keys(_data["fields"].get("Other Taxable Amounts", ""))
            entered_value = other_taxable_input.get_attribute("value")
            print(f"Entered Other Taxable: {entered_value}")
            
            if "Other Taxable Description" in _data["fields"]:
                other_taxable_desc_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxableDesc")
                other_taxable_desc_input.clear()
                other_taxable_desc_input.send_keys(_data["fields"].get("Other Taxable Description", ""))  # 새로운 값 입력
                entered_value = other_taxable_desc_input.get_attribute("value")
                print(f"Entered Other Taxable Description: {entered_value}")
            else:
                other_taxable_desc_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxableDesc")
                other_taxable_desc_input.clear()
                other_taxable_desc_input.send_keys("ADMIN/OMVIC")
                entered_value = other_taxable_desc_input.get_attribute("value")
                print(f"Entered Other Taxable Description: {entered_value}")


# 'Other Non-Taxable' 입력 필드 찾기
# other_non_taxable_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherNonTaxable")

# 'Other Non-Taxable Description' 입력 필드 찾기
# other_non_taxable_desc_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherNonTaxableDesc")

##################################################### Aftermarket Service #################################################################
###########################################################################################################################################
# 'Extended Warranty' 입력 필드 찾기
# extended_warranty_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtExtendedWarranty")

# 'Extended Warranty Term' 선택 필드 찾기
# ex_warranty_term_select = Select(driver.find_element(By.ID, "ctl21_ctl30_ctl00_ddlExWarrantyTerm"))

# 'Replacement Warranty' 입력 필드 찾기
# replacement_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtReplacement")

# 'Life Insurance' 입력 필드 찾기
# life_insurance_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtLifeInsurance")

# 'AH Insurance' 입력 필드 찾기
# Gap Insurance Amount
if "Gap Insurance Amount" in _data["fields"]:
    ah_insurance_input = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl30_ctl00_txtAHInsurance")))
    ah_insurance_input.click()
    ah_insurance_input.send_keys(str(_data["fields"].get("Gap Insurance Amount", "")))
    entered_value = ah_insurance_input.get_attribute("value")
    # Tab 키로 필드 벗어나기
    ah_insurance_input.send_keys(Keys.TAB)
    print(f"Entered Gap Insurance Amount: {entered_value}")

################################################## Defereal and Payment Date Options ######################################################
###########################################################################################################################################



############################################################ Dealer Tools #################################################################
###########################################################################################################################################


###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################



###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

#드라이버 종료
# time.sleep(1)
# time.sleep(1)
# time.sleep(1)
# driver.quit()