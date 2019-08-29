from flask import Flask, escape, request
from database import Database

app = Flask(__name__)

@app.route('/addFlight', methods=['POST'])
def addFlight():
    flight_number = request.form.get('flight_number')
    departure_date = request.form.get('departure_date')
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    if not (flight_number and departure_date and origin and destination):
        return 'Fields missing, please try again.'
    return Database().addFlight(flight_number, departure_date, origin, destination)