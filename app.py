# Dependencies
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func

# Setups - Database
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

# Setups - Flask
from flask import Flask, jsonify
app = Flask(__name__) 

# References
Station = Base.classes.station
Measurement = Base.classes.measurement

# Routes

@app.route("/")
def home():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&ltstart&gt<br/>"
        "/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    
    """Return a dictionary all precipitation data based on date"""
    
    # Query Precipitation Data
    prcpQuery = session.query(Measurement.date, Measurement.prcp).all()
    prcpDict = dict(prcpQuery)
    session.close()
    return jsonify(prcpDict)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    
    """List all stations"""
    
    # Query Stations
    stationQuery = session.query(Station.station).all()
    stationList = list(np.ravel(stationQuery))
    session.close()
    return jsonify(stationList)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    
    """Lists Temp data from last year from most active station"""
    
    # Query Active Station
    activeQuery = session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc())
    activeStationId = activeQuery.first()[0]
    
    # Query Recent Date
    recDateQuery = session.query(func.max(Measurement.date)).first()[0]
    
    # Get Year Before
    dateList = list(recDateQuery)
    dateList[3] = '6'
    lastYear = "".join(dateList)
    print(recDateQuery)
    
    # Set Filters
    fil1 = Measurement.date <= recDateQuery
    fil2 = Measurement.date >= lastYear
    
    # Query Temp Data
    tempQuery = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == activeStationId).\
        filter(fil1 & fil2).\
        order_by(Measurement.date)
    tempDict = dict(tempQuery)
    session.close()
    return jsonify(tempDict)

@app.route('/api/v1.0/<start>')
def startDate(start):
    session = Session(engine)
    
    """Get Min, Avg, and Max Temp from Start Date"""
    
    # Set Filter
    fil1 = Measurement.date >= start
    
    # Query Temp Data with Filters
    dateQuery = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(fil1).first()
    
    # Setup Dictionary
    dateDict = dict()
    dateDict['TMIN'] = dateQuery[0]
    dateDict['TMAX'] = dateQuery[1]
    dateDict['TAVG'] = round(dateQuery[2], 1)
    session.close()
    return jsonify(dateDict)

@app.route('/api/v1.0/<start>/<end>')
def startEndDate(start, end):
    session = Session(engine)
    
    """Get Min, Avg, and Max Temp between Start and End date"""
    
    # Set Filter
    fil1 = Measurement.date >= start
    fil2 = Measurement.date >= end
    
    # Query Temp Data with Filters
    dateQuery = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(fil1 & fil2).first()
    
    # Setup Dictionary
    dateDict = dict()
    dateDict['TMIN'] = dateQuery[0]
    dateDict['TMAX'] = dateQuery[1]
    dateDict['TAVG'] = round(dateQuery[2], 1)
    session.close()
    return jsonify(dateDict)

# Extra
if __name__ == "__main__":
    app.run(debug=True)
