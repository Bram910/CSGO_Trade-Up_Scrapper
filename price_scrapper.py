from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pylightxl as xl
import Case_Skins as cls
import save_to_db as save

def search_skin(Cases, driver, displayVar, window):
    for case in Cases:
        for skin in case.Skins:

            print(f"Searching prices for: {skin.weapon} | {skin.name}")

            # Initialize all skin prices with -1
            skin.prices = [-1] * 11  # More efficient initialization

            try:
                input_element = driver.find_element(By.ID, 'searchInput')
                input_element.clear()
                input_element.send_keys(skin.weapon + ' ' + skin.name)
                input_element.send_keys(Keys.ENTER)
            except NoSuchElementException as e:
                print(f"Search input element not found: {e}")
                continue

            print(f"Waiting for page to load for skin: {skin.name}")
            print(f"Current URL after search: {driver.current_url}")  # Print the current URL after search

            try:
                # Wait for the page to load (wait until the skin name appears in the first box of the table)
                WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.XPATH, '//table/tbody/tr[1]'), skin.name))
                print(f"Page loaded for skin: {skin.name}")
            except TimeoutException:
                print(f"Timeout while waiting for page to load for skin: {skin.name}")
                print("Page source at timeout:")
                print(driver.page_source)  # Print page source to understand the issue
                continue  # Skip to the next skin

            # Calculate the average prices from the sites and add to the skin at the required quality
            for i in range(1, 11):
                try:
                    table_row = driver.find_element(By.XPATH, f'//table/tbody/tr[{i}]').text
                    data = table_row.split(' ')

                    # Count how many characters to skip to reach the prices
                    count = 0
                    for index, elem in enumerate(data):
                        if '(' in elem:
                            count = index + 1
                            break

                    if 'Dragon King' in table_row:
                        count += 2

                    plus1 = 0
                    if 'stattrak' in data[0].lower():
                        plus1 += 1

                    # Add the price to the required QUALITY
                    if '(FN)' in table_row:
                        skin.prices[plus1 * 5 + 0] = data[count]
                    if '(MW)' in table_row:
                        skin.prices[plus1 * 5 + 1] = data[count]
                    if '(FT)' in table_row:
                        skin.prices[plus1 * 5 + 2] = data[count]
                    if '(WW)' in table_row:
                        skin.prices[plus1 * 5 + 3] = data[count]
                    if '(BS)' in table_row:
                        skin.prices[plus1 * 5 + 4] = data[count]

                    print_to_log(f"{skin.weapon} | {skin.name} sells for {data[count]}$ on average.", displayVar, window)

                except NoSuchElementException:
                    print(f"{skin.name} not found in all qualities.")
                except Exception as e:
                    print(f"Unexpected error occurred while processing skin: {skin.weapon} | {skin.name}. Error: {e}")


# Will be called for each case
def read_xl(db, sheet_name, Cases):
    [roww, coll] = db.ws(sheet_name).size
    data = db.ws(sheet_name).range('A2:N' + str(roww))
    for row in data:
        ObjSkin = cls.Skin()
        ObjSkin.name = row[0]
        ObjSkin.weapon = row[1]
        ObjSkin.rarity = row[2]
        Cases.Skins.append(ObjSkin)

def print_to_log(text, text_Var, window):
    text_Var.set(text_Var.get() + '\n' + text)
    window.update()

def extract_prices(input_file, output_file, displayVar, window):
    print("Extracting prices...")
    Cases = []
    db = xl.readxl(input_file)
    sheet_names = db.ws_names

    for sheet in sheet_names[1:]:
        ObjCase = cls.Case()
        ObjCase.name = sheet
        read_xl(db, sheet, ObjCase)
        Cases.append(ObjCase)

    print(f"Found {len(Cases)} cases.")

    # Adding some settings to make Chrome not open in test mode (as Selenium opens it)
    # because without this I wouldn't be able to pass Cloudflare verification
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    driver.get('https://csgo.steamanalyst.com/markets')

    # I need 13 seconds to create a new Chrome tab to open the same link
    # In this new tab, I will pass Cloudflare verification, and then the page will load on the working tab
    # and the program can run without issues
    time.sleep(13)

    # Minimize the window and position it in an inaccessible location
    # this way, if the user does not close the window, they cannot affect the search process
    driver.minimize_window()
    driver.set_window_position(-10000, -10000, windowHandle='current')

    search_skin(Cases, driver, displayVar, window)

    driver.close()

    save.to_xlsx(Cases, output_file, True)
