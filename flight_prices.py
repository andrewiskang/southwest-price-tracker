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
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
# specify the desired user agent
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(options=chrome_options, executable_path=os.getcwd() + '/chromedriver')


class FlightInfo(object):
    # contains all the necessary information to define a one-way flight:
    # flight #, departure date, origin, destination

    def __init__(self, flight_num, departure_dt, origin, destination):
        # return a FlightInfo object with the required parameters
        self.flight_num = flight_num
        self.departure_dt = departure_dt
        self.origin = origin
        self.destination = destination

    def print_info(self):
        # prints all information pertaining to the flight_num
        print("flight #:        " + str(self.flight_num))
        print("departure date:  " + str(self.departure_dt))
        print("origin:          " + self.origin)
        print("destination:     " + self.destination)

    def flightinfo_datastore(self):
        # stores flightinfo in Google Cloud Datastore
        datastore_client = datastore.Client()
        kind = "FlightInfo"

    def get_price(self):
        # opens southwest site, searches for specific flight price given params
        # returns output as a RecordedPrice object
        try_count = 0
        while try_count < 5:
            try:
                # point webdriver to Southwest website
                url = ("https://www.southwest.com/air/booking/select.html"
                     + "?int=HOMEQBOMAIR"
                     + "&adultPassengersCount=1"
                     + "&departureDate="+self.departure_dt
                     + "&departureTimeOfDay=ALL_DAY"
                     + "&destinationAirportCode="+self.destination
                     + "&fareType=USD"
                     + "&originationAirportCode="+self.origin
                     + "&passengerType=ADULT"
                     + "&promoCode="
                     + "&reset=true"
                     + "&returnDate="
                     + "&returnTimeOfDay=ALL_DAY"
                     + "&seniorPassengersCount=0"
                     + "&tripType=oneway"
                )
                driver.get(url)
                driver.implicitly_wait(10)
                print(url)

                # on next page, find all flight information and store them in array
                
                # wait for page to fully load
                try:
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.air-booking-select-detail")))
                except TimeoutException:
                    print("Timed out waiting for page to load")
                    try_count += 1
                    continue
                time.sleep(3)

                # following selects all flight elements
                flights = driver.find_elements_by_css_selector("li.air-booking-select-detail")

                # from flight elements, find the correct element (using flight num)
                for flight in flights:
                    number = flight.find_element_by_css_selector("span.actionable--text")
                    if number.text == ("# " + str(self.flight_num)):
                        selected_flight = flight
                        break

                # return error if flight not found
                if not selected_flight:
                    print("Flight could not be found!")

                else:
                    # locate WGA price
                    wga_element = selected_flight.find_element_by_css_selector("div.fare-button_primary-yellow")
                    wga_element = wga_element.find_element_by_css_selector("span.fare-button--value-total")
                    wga_price = wga_element.text

                    # return price with timestamp as a RecordedPrice object
                    return RecordedPrice(datetime.datetime.utcnow(), wga_price)

            except:
                print("There was an issue. Retrying...")
                try_count += 1

    def print_price(self):
        # prints out flight information as well as its current price
        price = self.get_price()
        self.print_info()
        price.print_info()

    def record_price(self):
        # records flight information to a CSV file
        # if file does not exist in directory, creates one
        if self.departure_dt <= datetime.datetime.utcnow().strftime("%Y-%m-%d"):
            print("Flight date has already passed or is today")
            
        else:
            # following opens/creates file for appending new timestamped price to
            with open("flight_prices/"+"_".join([self.departure_dt, self.origin, self.destination, self.flight_num])+".csv", "a+") as file:
                try:
                    current_price = self.get_price()
                    timestamp = str(current_price.timestamp)
                    price = current_price.price
                    
                    price_writer = csv.writer(file, delimiter=',')
                    price_writer.writerow([timestamp, price])
                except:
                    print("Exceeded number of attempts")


class RecordedPrice(object):
    # contains flight price and timestamp

    def __init__(self, timestamp, price):
        # return a RecordedPrice object with timestamped price
        self.timestamp = timestamp
        self.price = price

    def print_info(self):
        # prints the timestamp and recorded price
        print("timestamp:       " + str(self.timestamp))
        print("flight price:    " + self.price)



if (len(sys.argv) != 5):
    print('error')
else:
    flight = FlightInfo(sys.argv[1], datetime.datetime.strptime(sys.argv[2], "%m/%d/%y").strftime("%Y-%m-%d"), sys.argv[3], sys.argv[4])
    flight.print_price()

driver.quit()

# end product:
#  - read from a file all flights whose prices should be checked
#  - for each flight, record current price to CSV (separate files for each flight)
#  - alert user if price drops, compared to the last recorded price
#  - scheduled via cron to automate and run regularly

# with open("flights.csv") as file:
#     flight_reader = csv.reader(file, delimiter=',')
#     for row in flight_reader:
#         f = FlightInfo(row[0], datetime.datetime.strptime(row[1], "%m/%d/%y").strftime("%Y-%m-%d"), row[2], row[3])
#         f.print_info()
#         record_price(f)