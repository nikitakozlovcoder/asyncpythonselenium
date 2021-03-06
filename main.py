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
links = set()

password = sys.argv[4]
username = sys.argv[5]
video_fetch = sys.argv[2] == "yes"
page_url = sys.argv[1]
def find_links(driver):
    links_els = driver.find_elements_by_xpath("//a[starts-with(@href, '/p/')]")
    for elem in links_els:
        links.add(elem.get_attribute("href"))
        print(elem.get_attribute("href"))


def infinite_scroll(driver):
    SCROLL_PAUSE_TIME = 1.25
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        find_links(driver)
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def login(driver):
    driver.get('https://www.instagram.com')
    wait = WebDriverWait(driver, 10)
    driver.find_element_by_css_selector('.rgFsT')
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "KPnG0")))  # util login page appear

    user = driver.find_element_by_name("username")

    passw = driver.find_element_by_name('password')

    ActionChains(driver)\
        .move_to_element(user).click()\
        .send_keys(username)\
        .move_to_element(passw).click()\
        .send_keys(password)\
        .perform()

    login_button_ = driver.find_element_by_xpath(
        "//form[@class='HmktE']/div/div[3]/button")
    login_button_.click()

async def download_file(file, ext):
      
    async with aiohttp.ClientSession() as s:
            resp = await s.get(file)
            if resp.status == 200:
                f = await aiofiles.open('D:/Applications/p/done/' + str(uuid.uuid4()) + ext, mode='wb')
                out = await resp.read()
               
                await f.write(out)
                await f.close()     

async def proceed_link(page_link, driver):
    driver.get(page_link)
    images_links = set()
    videos_links = set()
    try:
        right = driver.find_element_by_css_selector(".coreSpriteRightChevron")
    except:
        pass
    
   

    while True:
        imgs = driver.find_elements_by_css_selector(".ltEKP img.FFVAD")
        if video_fetch:
            videos = []
            previews = []

            try:
                videos = driver.find_elements_by_css_selector(".tWeCl")
                previews = driver.find_elements_by_css_selector("._8jZFn")
            except:
                pass
            
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
    print(images_links)
    first_bank = asyncio.gather(*[download_file(file, '.jpg') for file in images_links])    
    second_bank = asyncio.gather(*[download_file(file, '.mp4') for file in videos_links])
    await first_bank 
    await second_bank
    
async def main():
    driver = webdriver.Chrome()
    login(driver)
    time.sleep(5)
    driver.get(page_url)

    total_expecting = driver.find_element_by_css_selector('.g47SY').text
    
    infinite_scroll(driver)

    if video_fetch:
        driver.delete_all_cookies()
    
    print(str(len(links))+"/"+total_expecting)

    #for link in links:
    #    proceed_link(link, driver)
    await asyncio.gather(*[proceed_link(link, driver) for link in links])
   
    print("DONE!")
    
   

asyncio.run(main())

