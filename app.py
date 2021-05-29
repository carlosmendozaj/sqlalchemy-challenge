
# Imports Dependencies
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
import sqlalchemy

import datetime as dt
import numpy as np

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

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"HOME<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start/<start> <br/>"
        f"/api/v1.0/start-end/<start>/<end> <br/>"
    )

#Precipitation:
@app.route("/api/v1.0/precipitation")
def precipitations():

    #Create sesion
    session = Session(engine)

    #Query Precipitation results
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    #Dictionaty for Precipitation
    all_prec = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict["date"] = date
        prec_dict["prcp"] = prcp
        all_prec.append(prec_dict)

    return jsonify(all_prec)

#Stations:
@app.route("/api/v1.0/stations")
def stations():

    #Create sesion
    session = Session(engine)

    
    #List for stations
    all_stations = session.query(Station.station).all()
    session.close()

    return jsonify(all_stations)

#TOBS 
@app.route("/api/v1.0/tobs")
def tobs():

    #Create sesion
    session = Session(engine)

    #Query stations
    tobs_result = session.query(Measurement.tobs).\
            filter(Measurement.station == "USC00519281").\
            filter(Measurement.date > "2016-08-18").all()
            
    
    session.close()

    #List of stations
    all_tobs = list(np.ravel(tobs_result))

    return jsonify(all_tobs)

#Start range
@app.route("/api/v1.0/<start>")
def start_date(start):

    #Create sesion
    session = Session(engine)

    most_active = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        all()
    most_active = most_active[0]

    sel = [ Measurement.date, 
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)
           ]
    
    results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.station == most_active).\
            order_by(Measurement.date).\
            all()       

    session.close()

    all_info = list(np.ravel(results))

    return jsonify(all_info) 

#Start-End Range
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    session = Session(engine)

    sel = [ Measurement.date, 
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)
           ]
    
    results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).\
            group_by(Measurement.station).\
            order_by((Measurement.date).desc()).\
            all()
        
    session.close()

    all_info = [{"date":result[0], "min":result[1], "avg":result[2], "max":result[3]} for result in results]

    return jsonify(all_info)


if __name__ == "__main__":
    app.run(debug=True)   

