import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
import time
import json
import re

# 변경할 변수 5가지
chrome_driver_path = "chromedriver/chromedriver.exe"  # 사용자의 ChromeDriver 경로로 변경하세요.
base_url = f"https://www.musinsa.com/search/goods?keyword=%ED%94%8C%EB%A0%88%EC%96%B4%EC%8A%A4%EC%BB%A4%ED%8A%B8&keywordType=keyword&gf=A&category=100006" #링크 바꾸세요
large_category = "SKIRTS" #채우세요
medium_category="LONG" #채우세요
small_category="FLARE" #채우세요
endpoint = 2000

#https://www.musinsa.com/app/goods/362514

# # Chrome 옵션 설정
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")  # 헤드리스 모드
# chrome_options.add_argument("window-size=1920,1080")  # 최대화된 상태의 크기로 설정
# chrome_options.add_argument("--log-level=3")  # WARNING 이상의 로그만 출력

service = Service(executable_path=chrome_driver_path)
# driver = webdriver.Chrome(service=service, options=chrome_options)
# 브라우저 창을 전체 화면으로 설정
driver = webdriver.Chrome(service=service)
driver.maximize_window()

file_name_prefix = large_category + "_" + medium_category + "_" + small_category

table_keys=["핏","촉감","신축성","비침","두께","계절"]

def save_cloth_info(cnt):
    try:
        info_table = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.sc-v134d5-6.gaPTWL")))
        li_elements = info_table.find_elements(By.TAG_NAME,"tr")

        data_dict = {}

        data_dict["file_num"]=cnt
        data_dict["file_name"] = file_name_prefix + f"_images_{cnt}.jpg"
        data_dict["large_category"]=large_category
        data_dict["medium_category"]=medium_category
        data_dict["small_category"]=small_category
        idx = 0
        for li in li_elements:
            try:
                key = table_keys[idx]
                values_li = li.find_elements(By.CSS_SELECTOR,"td.iwXmpA")
                values = []
                for value_li in values_li:
                    value=value_li.text
                    value = re.sub(r'\s+',' ',value)
                    values.append(value)
                data_dict[key] = values
                idx+=1

            except NoSuchElementException as e:
                print(f"요소(li)를 찾지 못했습니다")
                return False
            
        img_src=[]
        try:
            # id="swiper-wrapper-38f2210676c18ded8"인 div 요소 찾기
            img_divs = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'jtPNWB')]")))

            for img_div in img_divs:
                try:
                    inner_div = img_div.find_element(By.CSS_SELECTOR, "div.xxnjM")
                    img = inner_div.find_element(By.TAG_NAME, "img")
                    img_src.append(img.get_attribute("src"))
                except NoSuchElementException:
                    print(f"이미지를 찾지 못했습니다")
                    return False
                
        except (NoSuchElementException, TimeoutException):
            print(f"요소(inner_div)를 찾지 못했습니다")
            return False
        
        #폴더 없으면 만듦
        if not os.path.exists('musinsa_labeling'):
            os.makedirs('musinsa_labeling')
        if not os.path.exists('musinsa_product_images'):
            os.makedirs('musinsa_product_images')

        #이미지들 저장
        img_cnt = 0
        for img_url in img_src:
            #이미지 받기
            response = requests.get(img_url)
            if response.status_code != 200: #못 받아오면 넘기기
                continue
            #이미지 저장
            image_file_path = os.path.join('musinsa_product_images', f"{file_name_prefix}_image_{cnt}_{img_cnt}.jpg")
            with open(image_file_path, 'wb') as file:
                file.write(response.content)
            img_cnt += 1
        #모든 이미지 저장 실패 시 처리 코드
        if img_cnt == 0:
            print("이미지 저장 실패")
            return False

        #라벨링 파일 저장
        with open(os.path.join('musinsa_labeling', f"{cnt}_label_{file_name_prefix}.json"), 'w', encoding='utf-8') as json_file:
            json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

        return True

    except (NoSuchElementException, TimeoutException):
        print("표 없음")
        return False


try:
    # 무신사 신상품 베스트 페이지 접속
    driver.get(base_url)
    time.sleep(3)  # 페이지 로드 대기

    cnt = 1 #default = 1
    cnt_success = 0 #default = 0

    while cnt_success < endpoint:
        time.sleep(2)
        try:
            xpath = f'//a[@class="gtm-select-item" and @data-index="{cnt}"]'
            element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))

            # 요소가 있는 경우
            if element:
                # inner_div = element.find_element(By.CLASS_NAME, "sc-1yenj15-9.cZTsNj")
                # a_tag = inner_div.find_element(By.CSS_SELECTOR, "a.sc-1yenj15-12.jSDLVt")
                href_value = element.get_attribute("href")
                # print(f"{cnt}:{href_value}")

                #새탭으로 제품페이지 열기
                driver.execute_script(f'window.open("{href_value}")')
                driver.switch_to.window(driver.window_handles[-1])
                
                try:
                    #경고창 있으면 바로 실패 처리
                    alert = Alert(driver)
                    alert_text = alert.text
                    print(f"Alert text: {alert_text}")
                    alert.accept()
                    print(f"{cnt} 실패")
                except NoAlertPresentException:
                    #경고창 없으면 정상 진행
                    if save_cloth_info(cnt_success):
                        print(f"{cnt} 성공({cnt_success})")
                        cnt_success+=1
                    else:
                        print(f"{cnt} 실패")
                
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                cnt += 1

        except (NoSuchElementException, TimeoutException):
            driver.execute_script("window.scrollBy(0, 1000);")

except Exception as e:
    print(e)

finally:
    driver.quit()  # 브라우저 닫기