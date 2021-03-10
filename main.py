from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import sys
import asyncio
import aiohttp
import aiofiles
import uuid
import json

def configure():
    config = {}
    config['password'] = sys.argv[4]
    config['username'] = sys.argv[3]
    config['video_fetch'] = sys.argv[2] == "yes"
    config['page_url'] = sys.argv[1]
    config['is_single'] = config['page_url'].find('/p/') != -1
    print(config)
    return config

config = configure()

def find_links(driver, links):
    links_els = driver.find_elements_by_xpath("//a[starts-with(@href, '/p/')]")
    for elem in links_els:
        if(len(sys.argv) >= 6 and len(links) >= int(sys.argv[5])):
            return False
        push_link(links, elem.get_attribute("href"))
        print(elem.get_attribute("href"))      
    return True

def infinite_scroll(driver, links):
    SCROLL_PAUSE_TIME = 1.25
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        if(not(find_links(driver, links))):
            return
       
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def login(driver):
    driver.get('https://www.instagram.com')
    driver.find_element_by_css_selector('.rgFsT')
    wait = WebDriverWait(driver, 10)
    
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "KPnG0")))  # util login page appear

    user = driver.find_element_by_name("username")

    passw = driver.find_element_by_name('password')

    ActionChains(driver)\
        .move_to_element(user).click()\
        .send_keys(config['username'])\
        .move_to_element(passw).click()\
        .send_keys(config['password'])\
        .perform()

    login_button_ = driver.find_element_by_xpath(
        "//form[@class='HmktE']/div/div[3]/button")
    login_button_.click()

async def download_file(_file, ext):
      
    async with aiohttp.ClientSession() as s:
            resp = await s.get(_file)
            if resp.status == 200:
                f = await aiofiles.open('D:/Applications/p/done/' + str(uuid.uuid4()) + ext, mode='wb')
                out = await resp.read()
               
                await f.write(out)
                await f.close()     

async def proceed_link(page_link, driver):
    driver.get(page_link)
    images_links = set()
    videos_links = set()
    wait = WebDriverWait(driver, 10)
    
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ltEKP img.FFVAD, .tWeCl")))

    try:
        right = driver.find_element_by_css_selector(".coreSpriteRightChevron")
    except:
        pass
    
   

    while True:
        imgs = driver.find_elements_by_css_selector(".ltEKP img.FFVAD")
        print(imgs)
        if config['video_fetch']:
            videos = driver.find_elements_by_css_selector(".tWeCl")
            previews = driver.find_elements_by_css_selector("._8jZFn")
          
            for preview in previews:
                images_links.add(preview.get_attribute("src"))
            for video in videos:
                videos_links.add(video.get_attribute("src"))

        for img in imgs:
            images_links.add(img.get_attribute("src"))

        try:
            right.click()
        except:
            break
    print("proceed_link "+page_link)        
    print(images_links)
    print(videos_links)
    await asyncio.gather(*[download_file(_file, '.jpg') for _file in images_links])    
    await asyncio.gather(*[download_file(_file, '.mp4') for _file in videos_links])
   
def push_link(links, link):
    if(len(sys.argv)>=6):
        links.append(link)
        links = list(dict.fromkeys(links))
    else :
        links.add(link)
   
def init_links():
    if(len(sys.argv)>=6):
        return list()
    else :
        return set()

async def main():
    driver = webdriver.Chrome()
    login(driver)
    time.sleep(5)
    if config['is_single']:

        if config['video_fetch']:
            driver.delete_all_cookies()

        await proceed_link(config['page_url'], driver)

    else :
        
        driver.get(config['page_url'])
        total_expecting = driver.find_element_by_css_selector('.g47SY').text
        links = init_links()
        infinite_scroll(driver, links)
       
        if config['video_fetch']:
            driver.delete_all_cookies()
        
        print(str(len(links))+"/"+total_expecting)

        await asyncio.gather(*[proceed_link(link, driver) for link in links])
   
    print("DONE!")
    
   
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

