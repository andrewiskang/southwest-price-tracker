from __future__ import division

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
        print("flight #:        " + self.flight_num)
        print("departure date:  " + self.departure_dt)
        print("origin:          " + self.origin)
        print("destination:     " + self.destination)

class RecordedPrice(object):
    # contains flight price and timestamp

    def __init__(self, timestamp, price):
        # return a RecordPrice object with timestamped price
        self.timestamp = timestamp
        self.price = price

    def print_info(self):
        # prints the timestamp and recorded price



        
