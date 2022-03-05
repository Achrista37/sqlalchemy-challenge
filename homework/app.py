# importing dependencies

import datetime as dt
import numpy as np
from datetime import date, datetime, timedelta
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
session = Session(engine)

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


#################################################
# Flask Routes
#################################################

#display main options for API for route in the main page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date_yyyymmdd<br/>"
        f"/api/v1.0/startdate/enddate_yyyymmdd"
    )

#Create route to obtain Precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a series of precipitations"""
    # Query all passengers
    results_prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    #Create a dictionary with the date as key and prcp as the value
    precip = {date: prcp for date, prcp in results_prcp}
    return jsonify(precip)

#Create route to obtain a list of available Stations  
@app.route("/api/v1.0/stations")
def stations():
# Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a series of stations"""
    # Query all stations
    results_station = session.query(Station.name, Station.station).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for name_st, code in results_station:
        station_dict = {}
        station_dict["station_name"] = name_st
        station_dict["code"] = code
        all_stations.append(station_dict)
    return jsonify(all_stations)

#Create oute to obtain Temperatures (TOBS)

@app.route("/api/v1.0/tobs")
def tobs():
# Create our session (link) from Python to the DB
    session = Session(engine)
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    """Return a series of stations"""
    # Query all stations
    # to get the date a year from the last entry ( = 2016/08/23) and the station with the highest number of readings (USC00519281)
    # the SQLAlchemy data in the Jupyter Notebook was used
    tobs = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
           filter(and_(Measurement.date >= prev_year),\
                Measurement.station =="USC00519281").all()
    session.close()
    
    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for dates_tobs, tobs_tobs, station_tobs in tobs:
        tobs_dict = {}
        tobs_dict["dates_tobs"] = dates_tobs
        tobs_dict["tobs"] = tobs_tobs
        tobs_dict["station"] = station_tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

#create route to obtain date, max temp, min temp and average temp if start and end date are supplied
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date): 
    session = Session(engine)
    result_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(and_(
        Measurement.date <= end_date),
        Measurement.date >= start_date
        ).all()
    session.close()
    temp_list = []
    for min_temp, max_temp, avg_temp in result_temp:
         temp_dict ={}
         temp_dict["min_temp"] = min_temp
         temp_dict["max_temp"] = max_temp
         temp_dict["avg_temp"] = avg_temp
         temp_list.append(temp_dict)  
    return jsonify(temp_list)

#create route to obtain date, max temp, min temp and average temp if only the start date being supplied
@app.route("/api/v1.0/<start_date2>")
def calc_temps2(start_date2): 
    session = Session(engine)
    result_temp2 = session.query(func.min(Measurement.tobs),\
                                func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date2).all()
    session.close()
    temp2_list = []
    for min_temp2, max_temp2, avg_temp2 in result_temp2:
         temp2_dict ={}
         temp2_dict["min_temp"] = min_temp2
         temp2_dict["max_temp"] = max_temp2
         temp2_dict["avg_temp"] = avg_temp2
         temp2_list.append(temp2_dict)  
    return jsonify(temp2_list)

if __name__ == "__main__":
    app.run(debug=True)
