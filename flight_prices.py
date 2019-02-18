from __future__ import division
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import datetime
import sys
import csv
import time


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


def get_price(flight_info):
    # opens southwest site, searches for specific flight price given params
    # returns output as a RecordedPrice object
    try_count = 0
    while try_count < 5:
        try:
            # start up Chrome webdriver and point to Southwest website
            driver = webdriver.Chrome()
            driver.set_window_position(2000, 2000)
            driver.implicitly_wait(15)
            driver.get("https://www.southwest.com/air/booking/select.html"
                     + "?int=HOMEQBOMAIR"
                     + "&adultPassengersCount=1"
                     + "&departureDate="+flight_info.departure_dt
                     + "&departureTimeOfDay=ALL_DAY"
                     + "&destinationAirportCode="+flight_info.destination
                     + "&fareType=USD"
                     + "&originationAirportCode="+flight_info.origin
                     + "&passengerType=ADULT"
                     + "&promoCode="
                     + "&reset=true"
                     + "&returnDate="
                     + "&returnTimeOfDay=ALL_DAY"
                     + "&seniorPassengersCount=0"
                     + "&tripType=oneway")

            """# toggle one-way, not roundtrip
            one_way_button = driver.find_element_by_id("trip-type-one-way")
            one_way_button.click()

            # input origin
            origin_field = driver.find_element_by_id("air-city-departure")
            origin_field.click()
            origin_field.send_keys(Keys.BACK_SPACE)
            origin_field.send_keys(flight_info.origin)

            # input destination
            destination_field = driver.find_element_by_id("air-city-arrival")
            destination_field.click()
            destination_field.send_keys(Keys.BACK_SPACE)
            destination_field.send_keys(flight_info.destination)

            # input departure date and submit
            departure_dt_field = driver.find_element_by_id("air-date-departure")
            departure_dt_field.click()
            departure_dt_field.send_keys(Keys.BACK_SPACE)
            departure_dt_field.send_keys(str(flight_info.departure_dt))
            departure_dt_field.submit()"""

            
            # on next page, find all flight information and store them in array

            # wait for page to fully load
            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.air-booking-select-detail")))
            except TimeoutException:
                print("Timed out waiting for page to load")
                driver.quit()
                sys.exit()
            time.sleep(3)

            # following selects all flight elements
            flights = driver.find_elements_by_css_selector("li.air-booking-select-detail")

            # from flight elements, find the correct element (using flight num)
            for flight in flights:
                number = flight.find_element_by_css_selector("span.actionable--text")
                if number.text == ("# " + str(flight_info.flight_num)):
                    selected_flight = flight
                    break

            # return error if flight not found
            if not selected_flight:
                print("Flight could not be found!")
                driver.quit()

            else:
                # locate WGA price
                wga_element = selected_flight.find_element_by_css_selector("div.fare-button_primary-yellow")
                wga_element = wga_element.find_element_by_css_selector("span.fare-button--value-total")
                wga_price = wga_element.text

                # quit the driver and close all associated windows
                driver.quit()

                # return price with timestamp as a RecordedPrice object
                return RecordedPrice(datetime.datetime.utcnow(), wga_price)

        except:
            print("There was an issue. Retrying...")
            driver.quit()
            try_count += 1

def print_current_price(flight_info):
    # prints out flight information as well as its current price
    price = get_price(flight_info)
    flight_info.print_info()
    price.print_info()

def record_current_price(flight_info):
    # records flight information to a CSV file
    # if file does not exist in directory, creates one
    if flight_info.departure_dt <= datetime.datetime.utcnow().strftime("%Y-%m-%d"):
        print("Flight date has already passed or is today")
        
    else:
        flight_num = str(flight_info.flight_num).replace(" / ", "+")
        departure_dt = str(flight_info.departure_dt)
        origin = flight_info.origin
        destination = flight_info.destination

        # following opens/creates file for appending new timestamped price to
        with open("flight_prices/"+"_".join([departure_dt, origin, destination, flight_num])+".csv", "a+") as file:
            try:
                current_price = get_price(flight_info)
                timestamp = str(current_price.timestamp)
                price = current_price.price
                
                price_writer = csv.writer(file, delimiter=',')
                price_writer.writerow([timestamp, price])
            except:
                print("Exceeded number of attempts")



# end product:
#  - read from a file all flights whose prices should be checked
#  - for each flight, record current price to CSV (separate files for each flight)
#  - alert user if price drops, compared to the last recorded price
#  - scheduled via cron to automate and run regularly

with open("flights.csv") as file:
    flight_reader = csv.reader(file, delimiter=',')
    for row in flight_reader:
        f = FlightInfo(row[0], datetime.datetime.strptime(row[1], "%m/%d/%y").strftime("%Y-%m-%d"), row[2], row[3])
        f.print_info()
        record_current_price(f)