from __future__ import division
from selenium import webdriver
import datetime

class FlightInfo(object):
    # contains all the necessary information to define a one-way flight:
    # flight #, departure date, origin, destination

    def __init__(self,flight_num, departure_dt, origin, destination):
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
        # return a RecordPrice object with timestamped price
        self.timestamp = timestamp
        self.price = price

    def print_info(self):
        # prints the timestamp and recorded price
        print("timestamp:       " + str(self.timestamp))
        print("flight price:    " + self.price)


def get_price(flight_info):
    # opens southwest site, searches for specific flight price given params
    # returns output as a RecordedPrice object

    # start up Chrome webdriver and point to Southwest website
    driver = webdriver.Chrome()
    driver.implicitly_wait(15)
    driver.get("https://www.southwest.com")

    # toggle one-way, not roundtrip
    one_way_button = driver.find_element_by_id("trip-type-one-way")
    one_way_button.click()

    # input origin
    origin_field = driver.find_element_by_id("air-city-departure")
    origin_field.clear()
    origin_field.send_keys(flight_info.origin)

    # input destination
    destination_field = driver.find_element_by_id("air-city-arrival")
    destination_field.clear()
    destination_field.send_keys(flight_info.destination)

    # input departure date and submit
    departure_dt_field = driver.find_element_by_id("air-date-departure")
    departure_dt_field.clear()
    departure_dt_field.send_keys(flight_info.departure_dt)
    departure_dt_field.submit()

    # on next page, search for tier elements for the given flight #
    # there should be 3 tiers: Business Select, Anytime, Wanna Get Away
    tiers = driver.find_elements_by_xpath("//*[contains(@title,'Departing flight " + str(flight_info.flight_num) + "')]")

    # select Wanna Get Away element and extract flight price from value
    # note from the value, we can extract additional elements like time
    wga_tier = tiers[-1]
    wga_elements = wga_tier.get_attribute("value").split("@")
    wga_price = wga_elements[11]

    # quit the driver and close all associated windows
    driver.quit()

    # return price with timestamp as a RecordedPrice object
    return RecordedPrice(datetime.datetime.utcnow(), wga_price)

def print_current_price(flight_info):
    # prints out flight information as well as its current price
    price = get_price(flight_info)
    flight_info.print_info()
    price.print_info()

print_current_price(FlightInfo(1809, "4/25/2018", "SFO", "LAS"))
