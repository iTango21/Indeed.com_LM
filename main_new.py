from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# importing the library
from bs4 import BeautifulSoup

import json
import time

from fake_useragent import UserAgent
from datetime import datetime
from calendar import monthrange
from pathlib import Path

ua = UserAgent()
ua = ua.random

import pandas as pd

# df = pd.read_csv(r'data\indeed.com_LM_2023-03-07T10-00-40.csv')
# df.to_json(r'data\new_test.json')


# #json_to_csv()
# df = pd.read_json(r'elements2.json')
# df.to_csv(r'elements2.csv', index=None)

# breakpoint()



# # # ================================================================================================================
# # # ================================================================================================================

def _my(file_):
    url = 'https://homeoffice.fm/wp-admin/profile.php'

    with open('config.json', 'r', encoding='utf-8') as set_:
        set_data = json.load(set_)

    set_email = set_data['set_email']
    set_pass = set_data['set_pass']

    print('start...')

    # # # START of "Init..."
    # # #
    chrome_path = "./chromedriver.exe"

    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--incognito")
    options.add_argument("start-maximized")
    #
    options.add_argument('--disable-blink-features=AutomationControlled')
    #
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    browser = webdriver.Chrome(options=options, executable_path=chrome_path)
    # # #
    # # # END of "Init..."

    # # # ===========================================================================================================
    # # # ===========================================================================================================

    # # # START of "login..."
    # # #
    browser.implicitly_wait(1.5)
    browser.get(url)
    time.sleep(2)

    email_xp = '//*[@id="user_login"]'
    in_email = browser.find_element(By.XPATH, email_xp)
    in_email.send_keys(set_email)
    time.sleep(1.1)

    pass_xp = '//*[@id="user_pass"]'
    in_pass = browser.find_element(By.XPATH, pass_xp)
    in_pass.send_keys(set_pass)
    time.sleep(1.2)

    checkbox_xp = '//*[@id="rememberme"]'
    checkbox = browser.find_element(By.XPATH, checkbox_xp).click()
    time.sleep(0.7)

    btn_login_xp = '//*[@id="wp-submit"]'
    btn_login = browser.find_element(By.XPATH, btn_login_xp).click()
    time.sleep(0.9)

    gear_xp = '//*[@id="wp-admin-bar-my-account"]/a'
    start_time = time.time()
    try:
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, gear_xp)))
    except:
        pass
    finish_time = time.time() - start_time
    print(finish_time)
    # # #
    # # # END of "login..."

    # # # ===========================================================================================================
    # # # ===========================================================================================================

    # # # START of "Collecting links..."
    # # #

    with open(r'data\new_test.json', 'r', encoding='utf-8') as set_:
        data_ = json.load(set_)

    set_Jobkey = data_['jobkey']

    for index in range(len(set_Jobkey)):

        i = str(index)



        # set_Jobkey = data_['jobkey'][str(index)]
        set_Title = data_['JobTitle'][str(index)]
        set_CompanyName = data_['CompanyName'][i]
        set_Location = data_['Location'][i]
        set_JobType = data_['JobType'][i]
        set_Description = data_['JobDescription'][i]
        set_URL = data_['CompanyWebsiteURL'][i]
        set_Logo_ = data_['CompanyLogo'][i]
        set_Logo = str(set_Logo_).split('/')[-1]
        set_DateFetched = data_['DateFetched'][i]

        #print(index, set_JobType[str(index)], end="\n")


        browser.implicitly_wait(1.5)

        url_start = 'https://homeoffice.fm/wp-admin/edit.php?post_status=draft&post_type=jb-job&paged=1'
        browser.get(url_start)
        time.sleep(5)

        url_new = 'https://homeoffice.fm/job-post/'
        browser.get(url_new)
        time.sleep(2)


        # Job Type *
        # job_type_arr = {
        #     "Freelance": "557",
        #     "Full-time": "554",
        #     "Graduate": "559",
        #     "Internship": "556",
        #     "Other": "698",
        #     "Part-time": "555",
        #     "Temporary": "558",
        #     "Volunteer": "560",
        #     "Indefined": "699"
        # }
        print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!   --->>>   {set_JobType}')
        type_xp = '//*[@id="job_type"]'
        sel = Select(browser.find_element(By.XPATH, type_xp))
        sel.select_by_visible_text(set_JobType)
        # sel.select_by_value(job_type_arr[set_JobType])
        time.sleep(1)

        # Title
        title_xp = '//*[@id="job_title"]'
        in_title = browser.find_element(By.XPATH, title_xp)
        in_title.send_keys(set_Title)
        time.sleep(1.1)

        # Location *
        location_xp = '//*[@id="job_location-0"]'
        in_Location = browser.find_element(By.XPATH, location_xp)
        in_Location.send_keys(set_Location)
        time.sleep(0.4)

        # Job Type *
        print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!   --->>>   {set_JobType}')
        type_xp = '//*[@id="job_type"]'
        #in_Type = browser.find_element(By.XPATH, type_xp)
        #in_Type.clear()
        # identify dropdown with Select class
        sel = Select(browser.find_element(By.XPATH, type_xp))
        # select by select_by_visible_text() method
        sel.select_by_visible_text(set_JobType)
        #in_Type.send_keys(set_JobType)
        time.sleep(0.5)



        # Job Category
        # "//*[@id="select2-job_category-container"]/span"

        # Job Description
        browser.switch_to.frame(browser.find_element(By.TAG_NAME, "iframe"))
        description_xp = '//*[@id="tinymce"]/p'
        in_description = browser.find_element(By.XPATH, description_xp)

        # Calculating result
        tmp_ = BeautifulSoup(set_Description)
        res = tmp_.get_text()

        in_description.clear()
        in_description.send_keys(res)
        time.sleep(0.3)

        # move out of frame to parent page
        browser.switch_to.default_content()
        time.sleep(1)

        # Application contact *
        url_xp = '//*[@id="job_application"]'
        in_url = browser.find_element(By.XPATH, url_xp)
        in_url.clear()
        in_url.send_keys(set_URL)
        time.sleep(0.5)

        # Company name *
        name_xp = '//*[@id="company_name"]'
        in_Name = browser.find_element(By.XPATH, name_xp)
        in_Name.clear()
        in_Name.send_keys(set_CompanyName)
        time.sleep(0.5)

        # Company website
        url_xp = '//*[@id="company_website"]'
        in_url = browser.find_element(By.XPATH, url_xp)
        in_url.clear()
        in_url.send_keys(set_URL)
        time.sleep(0.5)

        # Logo
        tmp1__ = browser.find_element(By.XPATH, '/html/body/main/div/div[1]/section[3]/div/div/div/div/div/div/form/div[15]/span/span[2]/span[1]/span[3]/div')
        tmp1_ = tmp1__.get_attribute("id")
        tmp1 = tmp1_.replace('_container', '')

        logo_xp = f'//*[@id="{tmp1}"]'
        in_logo = browser.find_element(By.XPATH, logo_xp)

        img_path = f'{set_Logo}.jpg'
        img_path = f'D:\\_work_\\programming\\Python\\0 _ freelance _ 0\\upw\\Indeed.com_LM\\img\\{set_Logo}.jpg'

        in_logo.send_keys(img_path)
        time.sleep(0.9)

        # Draft
        but_Draft_xp = '//*[@id="jb-job-draft"]'
        but_Draft = browser.find_element(By.XPATH, but_Draft_xp).click()
        time.sleep(0.5)


        # but_Preview_xp = '//*[@id="jb-job-preview"]'
        # but_Preview = browser.find_element(By.XPATH, but_Preview_xp).click()
        # time.sleep(0.5)

        # breakpoint()


    url_stop = 'https://homeoffice.fm/wp-admin/edit.php?post_status=draft&post_type=jb-job&paged=1'
    browser.get(url_stop)
    time.sleep(300)


    browser.close()
    browser.quit()




if __name__ == "__main__":
    _my('file.csv')


