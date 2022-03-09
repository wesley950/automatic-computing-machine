from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import By

import pandas as pd

driver : webdriver.Chrome = None
base_url_template = "https://www.floridabar.org/directories/find-mbr/?lName=&sdx=N&fName=&eligible=N&deceased=N&firm=&locValue=&locType=C&pracAreas=R01&lawSchool=&services=&langs=&certValue=&pageNumber=%d&pageSize=50"
profiles = []

def init():
    global driver
    driver = webdriver.Chrome(executable_path="./chromedriver")
    print("Application initialized...")

def visit_page(page_number: int):
    global driver
    page_address = base_url_template % (page_number, )
    print("Visiting Page:\n\t%s" % (page_address, ))
    driver.get(page_address)
    print("Waiting for list of profiles to appear...")
    WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CLASS_NAME, "profiles-compact")))

def add_profile_to_list(profile):
    global profiles
    profile_data = []

    profile_name = profile.find_element(By.CLASS_NAME, "profile-name")
    profile_name_link = profile_name.find_element(By.TAG_NAME, "a")
    contact_name = profile_name_link.text

    profile_contact = profile.find_element(By.CLASS_NAME, "profile-contact")
    profile_contact_info = profile_contact.find_elements(By.TAG_NAME, "p")
    profile_company_and_address = ""
    profile_phones_and_email = ""
    profile_caa = []
    profile_pae = []
    if len(profile_contact_info):
        profile_company_and_address = profile_contact_info[0]
        profile_phones_and_email = profile_contact_info[1]

        profile_caa = profile_company_and_address.text.split('\n')
        profile_pae = profile_phones_and_email.text.split('\n')

    profile_data.append(contact_name) # Person's name
    profile_data.append(", ".join(profile_caa)) # Work location(?)
    if len(profile_pae) >= 2:
        profile_data.append(profile_pae[0]) # Office phone number
        profile_data.append(profile_pae[-1]) # Worl email
    
    profiles.append(profile_data)
    print(contact_name)

def download_current_page():
    global driver

    profile_ul = driver.find_element(By.CLASS_NAME, "profiles-compact")
    if profile_ul == None:
        print("Could not find profiles on current page!")
        exit(-1)
    
    i = 0
    profile_ul = profile_ul.find_elements(By.CLASS_NAME, "profile-compact")
    print("Downloading info from %d profiles..." % (len(profile_ul), ))
    for profile_li in profile_ul:
        add_profile_to_list(profile_li)
    compile_pages()

def compile_pages():
    print("Saving to csv...")
    df = pd.DataFrame(profiles, columns=["Full Name", "Work Location", "Office Phone Number", "Work Email"])
    df.to_csv("./real estate attorneys.csv", index=False)

if __name__ == "__main__":
    init()
    for page_number in range(1, 86):
        visit_page(page_number)
        download_current_page()
    compile_pages()