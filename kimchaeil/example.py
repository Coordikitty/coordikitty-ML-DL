import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

import json

# 성별 정보를 추출하는 함수
def extract_gender_info(driver):
    spans = driver.find_elements(By.CSS_SELECTOR, 'span.product-detail__sc-achptn-4.cobjEx')
    for span in spans:
        text = span.text
        if text == '남성' or text == '여성':
            return text
        elif '남성' in text and '여성' in text:
            return '남성, 여성'
    return None

# 이미지 다운로드 및 정보 추출 함수
def download_image_and_extract_info(image_url_list, folder_name, num, driver):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    img_success = False
    img_list = []
    for image_url in image_url_list:
        response = requests.get(image_url)
        if response.status_code == 200:
            img_success = True
            img_list.append(response.content)
        
    if img_success:
        product_info = {
            "file_num": num,
            "file_name": f"image_{num}.jpg",
            "large_category":'하의',
            "medium_category":'긴바지',
            "small_category":'데님',
            "fit": [],
            "season": [],
            "sex": None,
            "major_style": "캐주얼",
            "minor_style": None
        }
        try:
            tbody = driver.find_element(By.CSS_SELECTOR, '#root > div.product-detail__sc-8631sn-0.gJskhq > div.product-detail__sc-8631sn-1.fPAiGD > div.product-detail__sc-8631sn-3.jKqPJk > div.product-detail__sc-17fds8k-0.PpQGA > table > tbody')
            rows = tbody.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                th_text = row.find_element(By.TAG_NAME, 'th').text
                if th_text == '핏':
                    fit_values = row.find_elements(By.CLASS_NAME, 'product-detail__sc-17fds8k-5.gpXliU')
                    for fit_value in fit_values:
                        product_info['fit'].append(fit_value.text)
                elif th_text == '계절':
                    season_values = row.find_elements(By.CLASS_NAME, 'product-detail__sc-17fds8k-5.gpXliU')
                    for season_value in season_values:
                        product_info['season'].append(season_value.text)
        except NoSuchElementException:
            print("Failed to extract fit and season information.")
            product_info['fit'].append('NaN')
            product_info['season'].append('NaN')

        # 성별 정보 추출
        product_info['sex'] = extract_gender_info(driver)
        
        # 'fit'과 'season' 정보가 모두 'NaN'인지 확인
        if product_info['fit'] == ['NaN'] and product_info['season'] == ['NaN']:
            print("Fit and season information missing. Skipping file download.")
            return False

        # JSON 파일로 저장
        if not os.path.exists('musinsa_labeling'):
            os.makedirs('musinsa_labeling')
        with open(os.path.join('musinsa_labeling', f"{num}_label.json"), 'w', encoding='utf-8') as json_file:
            json.dump(product_info, json_file, ensure_ascii=False, indent=4)

        img_cnt = 0
        for content in img_list:
            image_file_path = os.path.join(folder_name, f"image_{num}_{img_cnt}.jpg")
            with open(image_file_path, 'wb') as file:
                file.write(content)
            img_cnt += 1
        return True
    
    else:
        print(f"Failed to download")
        return False
        
# Chrome Driver 경로 설정
chrome_driver_path = "C:/Users/rlaco/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"  # 사용자의 ChromeDriver 경로로 변경하세요.
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# 브라우저 창을 전체 화면으로 설정
driver.maximize_window()

# 대기 시간 설정을 위한 WebDriverWait 객체 생성
wait = WebDriverWait(driver, 10)  # 최대 10초 대기

try:
    # 무신사 신상품 베스트 페이지 접속
    current_page_number=1
    base_url = f"https://www.musinsa.com/categories/item/003002?d_cat_cd=003002&brand=&list_kind=small&sort=pop_category&sub_sort=&page={current_page_number}&display_cnt=90&exclusive_yn=&sale_goods=&timesale_yn=&ex_soldout=&plusDeliveryYn=&kids=&color=&price1=&price2=&shoeSizeOption=&tags=&campaign_id=&includeKeywords=&measure="
    driver.get(base_url)
    # last_page = int(driver.find_element(By.XPATH,'//*[@id="goodsList"]/div[4]/span/span[1]').text)
    # last_page = int(driver.find_element(By.XPATH,'//*[@id="goodsList"]/div[4]/span/span[1]')) #검색페이지에서
    # last_page = int(driver.find_element(By.CLASS_NAME,'totalPagingNum').text)
    last_page = 12
    print(f"last_page={last_page}")
    idx = 1  # 이미지 인덱스
    while True:
        product_urls = []
        # 각 제품의 상세 페이지로 이동하는 링크 찾기
        product_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.list-box .li_inner .list_img a')))
        for link in product_links:
            product_urls.append(link.get_attribute('href'))

        for product_url in product_urls:
            driver.get(product_url)
            try:
                # first_image = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img[src*="goods_img"]')))
                # first_image_src = first_image.get_attribute('src')
                # print(f"Downloading {first_image_src}")
                li_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.product-detail__sc-p62agb-7.deRVDj > li')

                src_values = []

                for li in li_elements:
                    # `li` 요소를 클릭
                    li.click()
                    
                    # 클릭 이후의 로딩 대기
                    # 고유한 식별자를 가진 콘텐츠가 로드될 때까지 대기하는 것이 좋습니다.
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.product-detail__sc-p62agb-1.brrfxn img'))
                    )
                    
                    # 클릭 이후에 나타난 `div` 내의 `img` 요소 찾기
                    img = driver.find_element(By.CSS_SELECTOR, 'div.product-detail__sc-p62agb-1.brrfxn img')
                    src_values.append(img.get_attribute('src'))

                # 이미지 다운로드 및 정보 추출
                if download_image_and_extract_info(src_values, 'musinsa_product_images', idx, driver):
                    print(f"image{idx} done")
                    idx += 1
                else:
                    print(f"Skipping image{idx} due to missing information")
                    
            except TimeoutException:
                print(f"Image loading timed out for {product_url}")
            finally:
                # 상세 페이지에서 작업을 마치고 원래 페이지로 돌아감
                driver.back()
            time.sleep(1)

        # 다음 페이지로 이동, 페이지가 10의 자리일 때 로직 포함
        # current_page_number = int(driver.find_element(By.CSS_SELECTOR, '.paging-btn.btn.active').text)
        if current_page_number==last_page:
            print("crawl done")
            break
        current_page_number = current_page_number + 1
        print(f"page move to {current_page_number}")
        base_url = f"https://www.musinsa.com/search/musinsa/goods?q=%EC%8A%AC%EB%9E%99%EC%8A%A4&list_kind=small&sortCode=pop&sub_sort=&page={current_page_number}&display_cnt=0&saleGoods=false&includeSoldOut=false&setupGoods=false&popular=false&category1DepthCode=&category2DepthCodes=&category3DepthCodes=&selectedFilters=&category1DepthName=&category2DepthName=&brandIds=&price=&colorCodes=&contentType=&styleTypes=&includeKeywords=&excludeKeywords=&originalYn=N&tags=&campaignId=&serviceType=&eventType=&type=&season=&measure=&openFilterLayout=N&selectedOrderMeasure=&shoeSizeOption=&d_cat_cd=&attribute=&plusDeliveryYn="
        driver.get(base_url)
except Exception as e:
    print(e)
finally:
    driver.quit()  # 브라우저 닫기
