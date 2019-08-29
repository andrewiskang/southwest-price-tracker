import sys
import datetime
from flight import FlightInfo

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



class Database(object):
    def __init__(self):
        self.cred = credentials.Certificate('ServiceAccountKey.json')
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

    # record the current price of the specified flight
    def recordFlightPrice(self, id):
        flight = self.db.document('flights/'+id).get().to_dict()
        if flight is None:
            print('Flight does not exist in database')
        elif flight['departure_date'].strftime('%Y-%m-%d') <= datetime.datetime.utcnow().strftime('%Y-%m-%d'):
            print('Flight date has already passed or is today')
        else:
            try:
                flightInfo = FlightInfo(flight['flight_number'], flight['departure_date'], flight['origin'], flight['destination'])
                price = flightInfo.getPrice()
                if price is None:
                    print('Price not found for the specified flight')
                self.db.collection('prices').add({
                    'flight_id': self.db.document('flights/'+id),
                    'price': price,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(e)

    # go through every flight in firestore and record their current prices
    def recordAllPrices(self):
        flights = db.collection('flights').stream()
        for flight in flights:
            data = flight.to_dict()
            self.recordFlightPrice(flight.id)

    # adds a flight with the given parameters
    def addFlight(self, flight_number, departure_date, origin, destination):
        return self.db.collection('flights').add({
            'flight_number': flight_number,
            'departure_date': departure_date,
            'origin': origin,
            'destination': destination
        })
