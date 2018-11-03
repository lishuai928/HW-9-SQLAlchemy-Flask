import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
    )

def parse_date(str):
    return dt.datetime.strptime(str, '%Y-%m-%d')

@app.route("/api/v1.0/precipitation")
def precipitation():
    """
    Convert the query results to a Dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary.
    """
    # Query 
    results = session.query(Measurement.date, Measurement.prcp).all()
    dict = {}
    for result in results:
        dict[result.date] = result.prcp

    return jsonify(dict)

@app.route("/api/v1.0/stations")
def stations():
    """
    Return a JSON list of stations from the dataset.
    """
    # Query 
    results = session.query(Station.station).all()
    list = []
    for result in results:
        list.append(result)
    return jsonify(list)

if __name__ == "__main__":
    app.run(debug=True)