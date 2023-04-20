#!/usr/bin/env python
# coding: utf-8
"""
Data-driven Portfolio Management 
Part 1: Web Scrapping

Group 4: 
Nicolás Amigo Sañudo
Gema Díaz Ferreiro
Rafael Sojo García
Stephan Wolters Eisenhardt

Python script related to the first web scrapping part of the assigment.
The code contains some context-specific function to facilitate the readibility,
but the main structure is within  if __name__ == "__main__"

All functions serve a special purpose for an in-depth data visualization analysis
all of which are described in detail in the corresponiding docstrings.


Overview of libraries used:

pandas (pd): The pandas library is used to handle the input data as a DataFrame. 
Functions like load_file use it to read the CSV file, while other functions use 
it for filtering and grouping the data.

numpy (np): Numpy is used for numerical operations and generating sequences. 
For example, in the return_distribution_area function, it is used to create an 
evenly spaced range of values for the x-axis.

time: Python built-in package.

selenium.webdriver.support.ui.WebDriverWait: This class is used for waiting 
a certain ammount of tiem during the accesing attemps to any HTML element given a driver

selenium.webdriver.support.expected_conditions(EC): An expectation for checking that an element 
is present on the DOM of a page and visible. Visibility means that the element is not only displayed 
but also has a height and width that is greater than 0.

selenium.webdriver.common.by.By: Set of supported locator strategies.

selenium.webdriver.common.action_chains.ActionChains: Class to enable longs concatenations of 
actions before the actual execution

selenium.webdriver.common.keys.Keys: Set of supported keyboard keys


"""

# In[6]:
import pandas as pd
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os


# In[7]:

#urls and filenames
URLS = [
    'https://www.investing.com/funds/amundi-msci-wrld-ae-c',
    'https://www.investing.com/etfs/db-x-trackers-ii-global-sovereign-5',
    'https://www.investing.com/etfs/ishares-global-corporate-bond-$',
    'https://www.investing.com/etfs/spdr-gold-trust',
    'https://www.investing.com/indices/usdollar'
]


FILENAMES = [
    'webscraping/amundi-msci-wrld-ae-c.csv',
    'webscraping/db-x-trackers-ii-global-sovereign-5.csv',
    'webscraping/ishares-global-corporate-bond-$-historical-data.csv',
    'webscraping/spdr-gold-trust.csv',
    'webscraping/usdollar.csv'
    ]

# start and end dates
STARTDATE_STR = "01/01/2020"
ENDDATE_STR = "12/31/2020"
STARTDATE_ARR = [2020,1,1]
ENDDATE_ARR = [2020,12,31]

# Xpaths of the elements within the else
STARTDT_EXPATH = "//div[@class='HistoryDatePicker_HistoryDatePicker__sjrlU']/div[1]/div/div[1]"
ENDDT_EXPATH = "//div[@class='HistoryDatePicker_HistoryDatePicker__sjrlU']/div[1]/div/div[2]"
APPLYBTN_EXPATH = "//div[@class='HistoryDatePicker_footer__KBy9B']/button" 
RANGEPICKER_ECSS = "DatePickerWrapper_input-text__PDRoD.DatePickerWrapper_center__zPpJy"
GETTABLE_EXPATH = '//table[@data-test="historical-data-table"]'


# In[8]:
def select_date(dateObj, wantedDate: list ):
    """
    Function to select the date by hovering over the calendar
    
    This funciton is used for the cases where the use of send_keys() is not possible due to the HTML format.
    It hovers over the calendar by pressing keys of the keyboard after clicking at each date element, and 
    moves according to current date and difference between the desired one.
    
    Args:
        dateObj: date element from the HTML 
        wantedDate: wanted date list with format YY/MM/DD

    Returns:
        None

    Raises:
        None

    Example:
        >>> date_input = some_element.find_element(By.XPATH, Expath+"/input")
        >>> select_date(date_input, [2020,12,31])
    """

    
    # prepare chain of actions
    action.move_to_element(dateObj)

    # It is needed to click 2 times since in some ocasions the finish date is by default +1 of the 
    # last clickable object. This way it is fixed.
    action.send_keys(Keys.ENTER)
    action.click()
    action.perform()

    # hover to the year/month selection
    for n in range(2):
        action.send_keys(Keys.TAB)
    action.send_keys(Keys.ENTER)


    # calculate the difference between the desired date and the actual date
    currtDate = np.array(dateObj.get_attribute("value").split('-'), dtype=int)
    year = abs(currtDate[0] - wantedDate[0])
    mnth = currtDate[1] - wantedDate[1]
    day = currtDate[2] - wantedDate[2]

    # move to selected year
    for n in range(year):
        for k in range(3):
            action.send_keys(Keys.ARROW_UP)

    # move to selected month
    for nj in range(abs(mnth)):
        if mnth>0:
            action.send_keys(Keys.ARROW_LEFT)
        else:
            action.send_keys(Keys.ARROW_RIGHT)

    # enter into the month and move to selected day
    action.send_keys(Keys.ENTER)
    for nd in range(abs(day)):
        if day>0:
            action.send_keys(Keys.ARROW_LEFT)
        else:
            action.send_keys(Keys.ARROW_RIGHT)

    # enter date      
    action.send_keys(Keys.ENTER)
    action.perform()
        


# In[9]:
def prepare_Edate(Expath, date_Arr):
    """
    Date inputation controller for assets different from amundi
    
    This funciton acts as the main controller for the steps required to 
    set the date in the assets different from amundi, since they require 
    a more complex management
    
    Args:
        Expath: XPATH of the date clickable element
        date_Arr: wanted date list with format YY/MM/DD

    Returns:
        None

    Raises:
        None

    Example:
        >>> prepare_Edate(SOME_XPATH, [2020,12,31])
    """
    
    date_field = wait_and_click(By.XPATH, Expath)
 
    # open and select the date by hovering through the dropdown. It is a dynamic
    # object that is generated with a javascript file and cannot be accesed 
    date_input = date_field.find_element(By.XPATH, Expath+"/input")
    select_date(date_input, date_Arr)


# In[10]:
def wait_and_click(by, path, t=5):
    """
    Function to call WebDriverWait, click and wait.
    
    This function acts as a simplification of the 3 steps: take element, click and wait. Since this steps are repeated
    several times, this way the code is simplified.
    
    Args:
        by: How the element is acces. See By from selenium.webdriver.common.by
        path: Path to the element in the correct format with respect by
    Returns:
        element: If accesed, it returns the element.

    Raises:
        None

    Example:
        >>> wait_and_click(By.ID, "some_id")
    """
    
    element = WebDriverWait(driver, t).until(
            EC.visibility_of_element_located((by, path))
        )
    # Click on the date range widget to open the calendar
    element.click()
    time.sleep(1)
        
    return element

# In[11]:
if __name__ == "__main__":

    for asset_url, asset_filename in zip(URLS, FILENAMES):

        # Preparations
        driver = webdriver.Chrome()  
        driver.get(asset_url + "-historical-data")
        action = ActionChains(driver)

        # Full screen just for commodity
        driver.fullscreen_window()
        time.sleep(1)

        # Accept cookie settings popup
        try:
            agree_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            agree_button.click()
        except Exception as e:
            print(f"Exception 1 occurred: {str(e)}")


        # wait for the popup to appear and close it
        try:
            wait_and_click(By.CSS_SELECTOR, "i.popupCloseIcon.largeBannerCloser",t=10)
        except Exception as e:
            print(f"Exception 2 occurred: {str(e)}")


        try:
            # Scroll down just for commodity
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.1);")
            time.sleep(1)

            #First iteration for amundi has different html structure
            if asset_url == URLS[0]:

                # Wait for date range picker to be visible 
                wait_and_click(By.ID, "widgetFieldDateRange")


                # Clear the start date input and enter a new date
                start_date_input = driver.find_element(By.ID, "startDate")
                start_date_input.clear()
                start_date_input.send_keys(STARTDATE_STR)

                end_date_input = driver.find_element(By.ID, "endDate")
                end_date_input.clear()
                end_date_input.send_keys(ENDDATE_STR)


                # Click apply button
                apply_button = driver.find_element(By.ID, "applyBtn")
                apply_button.click()
                time.sleep(1)

                # Get Table
                table = driver.find_element(By.ID, 'curr_table')


            #remaining iterations have same html structure
            else:

                # Wait for date range picker to be visible 
                wait_and_click(By.CLASS_NAME, RANGEPICKER_ECSS)


                # handle calendar widget
                prepare_Edate(STARTDT_EXPATH, STARTDATE_ARR)
                prepare_Edate(ENDDT_EXPATH, ENDDATE_ARR)


                # Click on the apply button
                apply_button = driver.find_element(By.XPATH, APPLYBTN_EXPATH)
                apply_button.click()
                time.sleep(1)

                # Get Table
                table = driver.find_element(By.XPATH, GETTABLE_EXPATH)

        except Exception as e:
            print(f"Exception 3 occurred: {str(e)}")


        table_html = table.get_attribute('outerHTML')
        driver.close()

        # Convert to CSV and download to work directory 
        if not os.path.exists('./webscraping'):
            os.mkdir('./webscraping')
        pd.read_html(table_html)[0].to_csv(asset_filename, index=False)


