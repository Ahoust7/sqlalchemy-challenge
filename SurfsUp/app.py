#Climate App
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Start at the homepage.
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
    f"Aloha to the Honolulu, Hawaii Climate Analysis. Here are the available routes:<br/>"
    f"Precipation Data for One Year<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"<br/>"
    f"List of Stations<br/>"
    f"/api/v1.0/stations<br/>"
    f"<br/>"
    f"Temparature Observation for One Year<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"Start Date of Min, Avg, and Max Temperature for a specified date(Format:yyyy-mm-dd):<br/>"
    f"/api/v1.0/<start><br/>"
    f"<br/>"
    f"Start and End Date of Min, Avg, and Max Temparature for a specifid date(Format:yyyy-mm-dd/yyyy-mm-dd):<br/>"
    f"/api/v1.0/<start>/<end>")

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days =365)
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>= year_ago).all()
    session.close()

#Dictionary
    precip_data = []
    for date, prcp in results:
        precip_dict= {}
        precip_dict[date]=prcp
        precip_data.append(precip_dict)
    return jsonify(precip_data)

#Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.name, Station.station, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    station_df = []
    for name, station, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["Name"] = name
        station_dict["Station ID"]= station
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        station_df.append(station_dict)
    return jsonify(station_df)

#Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days =365)
    active_stations = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                filter(Measurement.date >= year_ago).all()
    session.close()

    most_active = []
    for date, temp in active_stations:
        active_dict = {}
        active_dict[date] = temp
        most_active.append(active_dict)
    return jsonify(most_active)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

@app.route("/api/v1.0/<start>")
def start (start):
    session = Session(engine)
    start_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
    session.close()

    start_date = []
    for min, max, avg in start_results:
        start_dict = {}
        start_dict["Minimum Temperature"] = min
        start_dict["Maximum Temparature"] = max
        start_dict["Average Temparature"] = avg
        start_date.append(start_dict)
    return jsonify(start_date)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    start_end_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    se_date = []
    for min, max, avg in start_end_results:
        se_dict= {}
        se_dict["Minimum Temparature"] = min
        se_dict["Maximum Temparature"] = max
        se_dict["Average Temparature"] = avg
        se_date.append(se_dict)
    return jsonify(se_date)
    
if __name__ == '__main__':
    app.run(debug=True)
