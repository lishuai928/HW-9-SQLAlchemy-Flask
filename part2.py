import numpy as np
import pandas as pd
import datetime as dt

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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start day'<br/>"
        f"/api/v1.0/'start day'/'end day'<br/>"
    )

def format_date(str):
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

@app.route("/api/v1.0/tobs")
def tobs():
    """
    query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year.
    """
    # Query
    measurement_date=session.query(Measurement.date).order_by(Measurement.date.desc()).all()
    last_day=pd.DataFrame(measurement_date).iloc[0,0]
    frist_day = dt.datetime.strptime(last_day,'%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date,Measurement.tobs).\
              filter(Measurement.date>=frist_day).\
              order_by(Measurement.date).all()
    
    list = []
    for result in results:
        list.append({'date':result.date, 'tobs': result.tobs})
    return jsonify(list)

@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def start(start, end):
    """
    Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    """
    data = session.query(func.min(Measurement.tobs).label("min"), \
                         func.avg(Measurement.tobs).label("avg"), \
                         func.max(Measurement.tobs).label("max")).\
                         filter(Measurement.date >= format_date(start))
    if end is not None:
        data = data.filter(Measurement.date <= format_date(end))

    results = data.all()
    list = []
    for result in results:
        list.append({"TMIN": result.min, "TAVG": result.avg, "TMAX": result.max})
    return jsonify(list)

if __name__ == "__main__":
    app.run(debug=True)
    
