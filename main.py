from flask import Flask, escape, request, render_template
from database import Database
import datetime

db = Database()
app = Flask(__name__)



@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    return render_template('index.html', times=dummy_times)

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

@app.route('/updatePrices')
def updatePrices():
    if db.recordAllPrices():
        return 'Prices updated!'
    else:
        return 'Error occurred, prices were not correctly updated.'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
