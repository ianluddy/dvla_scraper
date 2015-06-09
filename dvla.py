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
LICENSE = 'YourLicense'
TEST_CENTRE = 'TestCentre'
ROOT = 'https://www.gov.uk/book-driving-test'
DRIVER = None
SLEEP = 120

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

def select_test_centre():
    DRIVER.find_element_by_id("search-results").find_element_by_tag_name("a").click()

def choose_test_centre():
    DRIVER.find_element_by_id("test-centres-input").clear()
    DRIVER.find_element_by_id("test-centres-input").send_keys(TEST_CENTRE)
    DRIVER.find_element_by_id("test-centres-submit").click()

def get_available_dates():
    return [slot.text for slot in DRIVER.find_elements_by_class_name("slotDateTime")]

def set_license_and_preferences():
    DRIVER.find_element_by_id("driving-licence").send_keys(LICENSE)
    DRIVER.find_element_by_id("extended-test-no").click()
    DRIVER.find_element_by_id("special-needs-none").click()
    DRIVER.find_element_by_id("driving-licence-submit").click()

def scrape():

    def element_found(element_id):
        try:
            return DRIVER.find_element_by_id(element_id) is not None
        except:
            return False

    create_driver()
    start()

    slots = None
    while not slots:

        if element_found("test-type-car"):
            choose_test()

        elif element_found("search-results"):
            select_test_centre()

        elif element_found("test-centres-input"):
            choose_test_centre()

        elif element_found("test-choice-calendar"):
            choose_date()

        elif element_found("driving-licence"):
            set_license_and_preferences()

        elif element_found("recaptcha-submit"):
            pass

        else:
            slots = get_available_dates()
            if slots:
                DRIVER.quit()
                return slots

        sleep(1)

def notify(slots):
    print slots
    return None
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

        sleep(SLEEP)

if __name__ == "__main__":
    run()