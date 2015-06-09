# Poll the DVLA website for newly available slots and email me when we find any
__author__ = 'iluddy'

from mailer import Message, Mailer
from selenium import webdriver
import datetime
from time import sleep
from random import randint

# Notifications
MAIL_SERVER = 'YourEmailServer'
MAIL = 'YourEmailAddress'

# Scraping
LICENSE = 'YourLicenseNumber'
TEST_CENTRE = 'YourTestCentrePreference'
ROOT = 'https://www.gov.uk/book-driving-test'
DRIVER = None

def today_string():
    return datetime.date.today().strftime("%d/%m/%y")

def create_driver():
    global DRIVER
    if randint(0, 10) >= 5:
        DRIVER = webdriver.Chrome('C:\\chromeDRIVER.exe')
    else:
        DRIVER = webdriver.Firefox()

def start():
    DRIVER.get(ROOT)
    DRIVER.find_element_by_id("get-started").find_element_by_tag_name("a").click()

def choose_date():
    DRIVER.find_element_by_id("test-choice-calendar").send_keys(today_string())
    DRIVER.find_element_by_id("driving-licence-submit").click()

def choose_test():
    DRIVER.find_element_by_id("test-type-car").click()

def choose_test_centre():
    DRIVER.find_element_by_id("test-centres-input").send_keys(TEST_CENTRE)
    DRIVER.find_element_by_id("test-centres-submit").click()
    DRIVER.find_element_by_id("search-results").find_element_by_tag_name("a").click()

def get_available_dates():
    return [slot.text for slot in DRIVER.find_elements_by_class_name("slotDateTime")]

def set_license_and_preferences():
    DRIVER.find_element_by_id("driving-licence").send_keys(LICENSE)
    DRIVER.find_element_by_id("extended-test-no").click()
    DRIVER.find_element_by_id("special-needs-none").click()
    DRIVER.find_element_by_id("driving-licence-submit").click()

def scrape():
    slots = None
    try:
        create_driver()
        start()
        choose_test()
        set_license_and_preferences()
        choose_test_centre()
        choose_date()
        slots = get_available_dates()
    finally:
        DRIVER.quit()
        return slots

def notify(slots):
    message = Message(From=MAIL, To=MAIL)
    message.Subject = "DVLA"
    message.Html = str([slot for slot in slots])
    sender = Mailer(MAIL_SERVER)
    sender.send(message)

def diff_slots(known, new):
    return list(set(new) - set(known))

def run():
    available_slots = None

    while True:
        # Get available slots [if this barfs it will return None and then we'll ignore it and try again]
        updated_slots = scrape()

        if updated_slots:
            # This is the first run so notify on what we have found
            if available_slots is None:
                notify(updated_slots)

            # Otherwise notify when we see new slots become available
            else:
                notify(diff_slots(available_slots, updated_slots))

            # Update availability and sleep
            available_slots = updated_slots

        sleep(30)

if __name__ == "__main__":
    run()