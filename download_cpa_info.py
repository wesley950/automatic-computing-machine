from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import By
from selenium.webdriver.common.keys import Keys

import pandas as pd

driver : webdriver.Chrome = None
# 0 Indexed!
base_template_url = "https://www.ficpa.org/resources-news/find-a-cpa?field_amnet_firm_county=All&field_amnet_industries=All&field_amnet_services=All&field_amnet_languages=All&is[industries]=All&so[services]=All&fl[languages]=All&fc[county]=All&page=%d"
accountants = []

def init() -> None:
    global driver
    driver = webdriver.Chrome(executable_path="./chromedriver")
    print("Initialized.")

def visit_page(page_number: int) -> None:
    global driver, base_template_url
    page_address = base_template_url % (page_number, )
    driver.get(page_address)
    print("Going to page:\n\t%s" % (page_address))

def get_accountant_email(link_elem) -> str:
    global driver
    result = ""
    current_tab = driver.current_window_handle
    link_elem.send_keys(Keys.CONTROL + Keys.ENTER)
    new_tab = driver.window_handles[1]
    driver.switch_to.window(new_tab)
    section = WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CLASS_NAME, "name_email_website")))
    try:
        email_link = section.find_element(By.TAG_NAME, "a")
        result = email_link.get_attribute("href")
    except:
        pass
    driver.close()
    driver.switch_to.window(current_tab)
    return result

def append_accountant(accountant_root_element) -> None:
    global driver, accountants
    accountant_link = accountant_root_element.find_element(By.TAG_NAME, "a")
    accountant_address = accountant_link.get_attribute("href")
    accountant_name = accountant_link.text
    info_divs = accountant_root_element.find_elements(By.CLASS_NAME, "item")
    accountant_phone = ""
    accountant_location = ""

    for info_div in info_divs:
        class_name = info_div.get_attribute("class")
        if class_name == "item firm-phone":
            accountant_phone = info_div.text
        elif class_name == "item firm-address":
            accountant_location = info_div.text
    
    accountant_email = get_accountant_email(accountant_link)

    accountants.append([accountant_name, accountant_email, accountant_phone, accountant_location])
    print(accountant_name)

def get_valid_accountants_in_page(accountants_in_page) -> list:
    result = []
    for accountant_in_page in accountants_in_page:
        try:
            accountant_in_page.find_element(By.TAG_NAME, "article")
            result.append(accountant_in_page)
        except:
            continue
    return result

def append_current_page() -> None:
    global driver, accountants
    list_of_accountants = WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[7]/div/section/div/div/div/div/div[2]/div[2]")))
    accountants_in_page = list_of_accountants.find_elements(By.CLASS_NAME, "col-md-12")
    accountants_in_page = get_valid_accountants_in_page(accountants_in_page)

    print("Adding %d accountants..." % (len(accountants_in_page), ))

    for accountant_in_page in accountants_in_page:
        append_accountant(accountant_in_page)

def save_to_file() -> None:
    global accountants
    print("Saving to csv...")
    headers = ["Name", "Email", "Phone", "Location"]
    df = pd.DataFrame(accountants, columns=headers)
    df.to_csv("florida certified public accountants.csv", index=False, mode="a", header=False)

if __name__ == "__main__":
    init()
    for page_number in range(2, 10):
        visit_page(page_number)
        append_current_page()
        save_to_file()