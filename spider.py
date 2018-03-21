import time
import pymongo
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import WebDriverException

#声明浏览器
browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)

#配置MongoDB数据库
client = pymongo.MongoClient('localhost')
db = client['Airbnb']

#访问主页，按要求搜索
def search(place,start,end):
    try:
        browser.get('https://zh.airbnb.com/')
        city = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#GeocompleteController-via-SearchBarLarge')))
        startdata = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#startDate')))
        enddata = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#endDate')))
        button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#site-content > div > div > div._jeonpt > div > div > div._ovebx1 > div > div > div > div > form > div > div:nth-child(4) > button > span')))
        city.send_keys(place)
        startdata.send_keys(start)
        enddata.send_keys(end)
        button.click()
        time.sleep(5)
        parse_page()
    except TimeoutError:
        print('请求失败')
        return search()

#翻页
def next_page():
    try:
        page = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#site-content > div > div > div._fk6lr88 > div > div > div > div > div:nth-child(4) > div._12to336 > div:nth-child(1) > nav > span > div > ul > li._b8vexar > a > div')))
        page.click()
        time.sleep(5)
        parse_page()
    except TimeoutError:
        print('翻页失败')
        return next_page()

#使用pyquery分析网页信息
def parse_page():
    try:
        html = browser.page_source
        doc = pq(html)
        items = doc('._fhph4u ._1mpo9ida').items()
        for item in items:
            hotel_title = item.find('._17djt7om').text()
            house_type = item.find('._saba1yg ._1cxs44em').text().replace('\n','').replace('\n','')
            house_price = item.find('._l8zgil6').text().replace('\n','')
            house_score = item.find('._1gvnvab').text()
            data = {
                'hotel':hotel_title,
                'type':house_type,
                'price':house_price,
                'score':house_score
            }
            save_to_mongo(data)
    except WebDriverException:
        return parse_page()

#存储到数据库MongoDB
def save_to_mongo(data):
    if db['nanjing'].insert(data):
        print('存储到MongoDB数据库成功',data)
    else:
        print('存储到MongoDB数据库失败',data)


def main():
    page = 1
    city = '南京'
    start = '3月22日'
    end = '3月23日'
    search(city,start,end)
    while page<17:
        print('正在爬取第{}页'.format(page))
        next_page()
        page+=1
        time.sleep(5)


if __name__ == '__main__':
    main()
