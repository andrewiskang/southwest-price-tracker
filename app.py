from flask import Flask, escape, request
from database import Database
db = Database()

app = Flask(__name__)

@app.route('/addFlight', methods=['POST'])
def addFlight():
    flight_number = request.form.get('flight_number')
    departure_date = request.form.get('departure_date') # must be in '%m/%d/%y' format
    origin = request.form.get('origin')
    destination = request.form.get('destination')

    # requires all four fields above
    if not (flight_number and departure_date and origin and destination):
        return 'Fields missing, please try again.'
    return db.addFlight(flight_number, departure_date, origin, destination)
