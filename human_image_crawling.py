import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time



# 이미지 다운로드 및 정보 추출 함수
def download_image_and_extract_info(image_url_list, folder_name, num):
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
        for content in img_list:
            image_file_path = os.path.join(folder_name, f"image_{num}.jpg")
            with open(image_file_path, 'wb') as file:
                file.write(content)
        return True
    
    else:
        print(f"Failed to download")
        return False
        
# Chrome Driver 경로 설정
chrome_driver_path = "C:/Users/mkmy7/OneDrive/바탕 화면/chromedriver-win64/chromedriver.exe"  # 사용자의 ChromeDriver 경로로 변경하세요.
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# 브라우저 창을 전체 화면으로 설정
driver.maximize_window()

# 대기 시간 설정을 위한 WebDriverWait 객체 생성
wait = WebDriverWait(driver, 10)  # 최대 10초 대기

try:
    # 무신사 신상품 베스트 페이지 접속
    current_page_number=1
    base_url = f"https://www.musinsa.com/mz/brandsnap?_m=&gender=&mod=&bid=&p={current_page_number}"
    driver.get(base_url)
    # last_page = int(driver.find_element(By.XPATH,'//*[@id="goodsList"]/div[4]/span/span[1]').text)
    # last_page = int(driver.find_element(By.XPATH,'//*[@id="goodsList"]/div[4]/span/span[1]')) #검색페이지에서
    # last_page = int(driver.find_element(By.CLASS_NAME,'totalPagingNum').text)
    last_page = 50
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
                if download_image_and_extract_info(src_values, 'musinsa_product_images', idx):
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
        base_url = f"https://www.musinsa.com/mz/brandsnap?_m=&gender=&mod=&bid=&p={current_page_number}"
        driver.get(base_url)
except Exception as e:
    print(e)
finally:
    driver.quit()  # 브라우저 닫기