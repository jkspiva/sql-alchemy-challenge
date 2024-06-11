# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

#create engine to hawaii.sqlite
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 1. /
# - Start at the homepage 
# - List all available routes

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter date as YYYY-MM-DD in place of 'start)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD in place of 'start' and 'end')"
)



# 2. /api/v1.0/precipitation
# - Convert the query results from your precipiation analysis (retrieve only the last 12 months
# of data) to a dictionary using 'date' as the key and 'prcp' as the value.
# - Return the JSON representation of your dictionary

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    last_12_months= dt.date(2017, 8, 23)-dt.timedelta(days=365)
    one_year_ago = dt.date(last_12_months.year, last_12_months.month, last_12_months.day)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    precipitation_dict = dict(results)

    print(f"Results for Precipitation - {precipitation_dict}")
    print("Out of Precipitation section.")
    return jsonify(precipitation_dict) 



# 3. /api/v1.0/stations
# - Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    query_result = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)



# 4. /api/v1.0/tobs
# - Query the dates and temperature observations of the most-active station for the previous year of data.
# - Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)

     result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date >='2016-08-23').all()

     tob_list = []
     for date, tobs in result:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob_list.append(tobs_dict)

     return jsonify(tob_list)



#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
# - Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# - For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# - For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)



if __name__ == '__main__':
    app.run(debug=True)
