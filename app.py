import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc, inspect

import datetime as dt
from datetime import datetime, time

from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

##===============================================#

# Flask Setup
app = Flask(__name__)


# Routes

# Home page.
# List all routes that are available.
@app.route("/")
def index_home():    
    return (
        f"<h1>Welcome to Surfs Up!</h1><br/>"
        f"<h2>Available Routes:</h2><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )


# /api/v1.0/precipitation
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():    
    
    results = session.query(Measurement).all()

    prcp_dict = {}
    for item in results:        
        prcp_dict[item.date] = item.prcp        

    return jsonify(prcp_dict)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():      

    results = session.query(Station).all()


    station_list = []
    for item in results:
        station_dict = {}
        station_dict["id"] = item.id
        station_dict["station"] = item.station
        station_dict["name"] = item.name
        station_dict["latitude"] = item.latitude
        station_dict["longitude"] = item.longitude
        station_dict["elevation"] = item.elevation

        station_list.append(station_dict)

    return jsonify(station_list)    


    # station_list = []
    # for item in results:        
    #     station_list.append([item.id, item.station, item.name, item.latitude, item.longitude, item.elevation])  
      
    # return jsonify(station_list)


# /api/v1.0/tobs
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs_year_last():
    
    # Latest Date
    result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = result[0]    

    # calculate the date one year before last measurement
    twelve_month_ago = dt.datetime.strftime((dt.datetime.strptime(latest_date,'%Y-%m-%d') - dt.timedelta(days=365)).date(),'%Y-%m-%d')
        
    # Debugging
    # return  '{} {}'.format(latest_date, twelve_month_ago)

    temp_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= twelve_month_ago).order_by(Measurement.date).all()
    
    temp_list = []
    for item in temp_result:
        temp_dict = {}
        temp_dict["date"] = item.date
        temp_dict["tobs"] = item.tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)
    


# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date>")
def startonly(start_date):

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()    

    temp_dict = {}
    temp_dict["Start Date"] = start_date
    temp_dict["TMIN"] = result[0][0]
    temp_dict["TAVG"] = result[0][1]
    temp_dict["TMAX"] = result[0][2]

    return jsonify(temp_dict)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all() 

    temp_dict = {}
    temp_dict["Start Date"] = start_date
    temp_dict["End Date"] = end_date
    temp_dict["TMIN"] = result[0][0]
    temp_dict["TAVG"] = result[0][1]
    temp_dict["TMAX"] = result[0][2]

    return jsonify(temp_dict)




if __name__ == "__main__":
    app.run(debug=True)