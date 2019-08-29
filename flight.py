from __future__ import division
import datetime
import sys
import os
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')



class FlightInfo(object):
    # contains all the necessary information to define a one-way flight:
    # flight #, departure date, origin, destination

    def __init__(self, flight_number, departure_date, origin, destination):
        # return a FlightInfo object with the given parameters
        self.flight_number = flight_number
        self.departure_date = departure_date
        self.origin = origin
        self.destination = destination

    def printInfo(self):
        # prints all information pertaining to the flight_number
        print('flight #:        ' + str(self.flight_number))
        print('departure date:  ' + str(self.departure_date))
        print('origin:          ' + self.origin)
        print('destination:     ' + self.destination)

    def getPrice(self):
        # opens southwest site, searches for and returns price of specified flight
        driver = webdriver.Chrome(options=chrome_options, executable_path=os.getcwd() + '/chromedriver')

        try_count = 0
        while try_count < 5:
            try:
                # point webdriver to Southwest website
                url = ('https://www.southwest.com/air/booking/select.html'
                     + '?int=HOMEQBOMAIR'
                     + '&adultPassengersCount=1'
                     + '&departureDate='+self.departure_date.strftime('%Y-%m-%d')
                     + '&departureTimeOfDay=ALL_DAY'
                     + '&destinationAirportCode='+self.destination
                     + '&fareType=USD'
                     + '&originationAirportCode='+self.origin
                     + '&passengerType=ADULT'
                     + '&promoCode='
                     + '&reset=true'
                     + '&returnDate='
                     + '&returnTimeOfDay=ALL_DAY'
                     + '&seniorPassengersCount=0'
                     + '&tripType=oneway'
                )
                driver.get(url)
                driver.implicitly_wait(10)

                # on next page, find all flight information and store them in array
                
                # wait for page to fully load
                try:
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.air-booking-select-detail')))
                except TimeoutException:
                    print('Timed out waiting for page to load')
                    try_count += 1
                    continue
                time.sleep(3)

                # following selects all flight elements
                flights = driver.find_elements_by_css_selector('li.air-booking-select-detail')

                # from flight elements, find the correct element (using flight num)
                for flight in flights:
                    number = flight.find_element_by_css_selector('span.actionable--text')
                    if number.text == ('# ' + str(self.flight_number)):
                        selected_flight = flight
                        break

                # return error if flight not found
                if not selected_flight:
                    print('Flight could not be found!')

                else:
                    # locate and return WGA price
                    wga_element = selected_flight.find_element_by_css_selector('div.fare-button_primary-yellow')
                    wga_element = wga_element.find_element_by_css_selector('span.fare-button--value-total')
                    wga_price = wga_element.text
                    driver.quit()
                    return wga_price

            except:
                print('There was an issue. Retrying...')
                try_count += 1

        # if end of function is reached, price was not found
        driver.quit()
