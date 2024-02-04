import os
import random
from time import sleep
import csv
from datetime import datetime
import pandas as pd
from random import randint

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    TimeoutException,
    WebDriverException,
)

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox

def open_browser():
    """
    Opens a new automated browser window with all tell-tales of automated browser disabled
    """
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("-headless")  # Enable headless mode
    
    # Remove all signs of this being an automated browser
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("marionette.enabled", True)

    # Open the browser with the new options
    driver = Firefox(options=options)
    return driver

while True:

    driver = open_browser()
    sleep(randint(5,15))

    print('going to the url')
    url = 'https://egov.uscis.gov/'
    driver.get(url)
    sleep(randint(5,15))

    search_box = driver.find_element(
        By.XPATH, 
        '//*[@id="receipt_number"]'
    )

    print('sending keys')
    search_term = os.environ.get('CASE_NUMBER')

    # search_box.send_keys('XXXXXXXX')

    search_box.send_keys(search_term)
    sleep(randint(5,15))

    case_status_box = driver.find_element(
        By.XPATH,
        '/html/body/div/div/main/div/div/div/div[1]/div[1]/button')

    case_status_box.click()

    def press_enter(driver):
        """
        Sends the ENTER to a webdriver instance.
        """
        actions = ActionChains(driver)
        actions.send_keys(Keys.ENTER)

#     actions.perform()
    
    sleep(randint(5,15))
    
    press_enter(driver)

    sleep(randint(5,15))

    status_section = driver.find_element(
        By.XPATH, 
        '/html/body/div/div/main/div/div/div/div[1]/div[1]/div[1]'
    )

    status = status_section.find_element(
        By.TAG_NAME, 'h2'
        ).text

    print(f'Status found: {status}')

    sleep(randint(5,15))

    if status == "Check Case Status":
        # If status is "Check Case Status," close the driver and restart the loop
        print("Status is 'Check Case Status.' Restarting from the beginning.")
        driver.quit()
        sleep(randint(5,15))
        continue  # Restart the loop

    else:
        break

# Now you can continue with the rest of your code
print("Status is different from 'Check Case Status'. Continuing with the code.")


# description = status_section.find_element(
#     By.TAG_NAME, 'p'
#     ).text

description = driver.find_elements(By.TAG_NAME, 'p')[4].text

print(f'Description found: {description}')

# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# # Check if the file "status_check.csv" exists
# file_exists = os.path.isfile("status_check.csv")

# # Create and open the CSV file for writing
# with open("status_check.csv", mode="a", newline="") as file:
#     fieldnames = ["Timestamp", "Status", "Description"]
#     writer = csv.DictWriter(file, fieldnames=fieldnames)

#     # If the file doesn't exist, write the header row
#     if not file_exists:
#         writer.writeheader()

#     # Write the data to the CSV file
#     writer.writerow({"Timestamp": timestamp, "Status": status, "Description": description})

# Create a dictionary with the data
data_dict = {
    'Timestamp': [timestamp],
    'Status': [status],
    'Description': [description]
}

# Create a DataFrame from the dictionary
data = pd.DataFrame(data_dict)
print('Updating .csv file')

# Read the last recorded `status` value from the CSV file
last_status = ""

try:
    df = pd.read_csv("status_check.csv")
    if not df.empty:
        last_status = df["Status"].iloc[-1]
        print(f'Last known status was {last_status}')
except FileNotFoundError:
    # Handle the case where the file doesn't exist initially
    pass



# Append the data to the existing CSV file (mode='a' for append)
data.to_csv('status_check.csv', mode='a', header=False, index=False)

df = pd.read_csv('status_check.csv')
# Get the number of rows in the DataFrame
n = len(df)

print(f'The csv file now has {n} rows.')


# Send email if case status has changed

if status != last_status:
    print('Statos has changed. Sending email')

    # Get the values of FROM_EMAIL and TO_EMAIL from environment variables
    from_email = os.environ.get('FROM_EMAIL')
    to_email = os.environ.get('TO_EMAIL')

    message = Mail(from_email=from_email,
                    to_emails=to_email,
                    subject='Update of status case USCIS' ,
                    plain_text_content=f'Your status changed from {last_status} to {status}')

    try:
        # Get the SendGrid API key from environment variables
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e.message)
else:
    print('Status has not changed')

# Close the WebDriver
driver.quit()