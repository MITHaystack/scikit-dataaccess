"""test_binned_tec.py does a single test of calling binned_tec
"""

# standard python imports
import datetime

# Millstone imports
import skdaccess.geo.tec.binned_tec.stream

# hard coded test values
user_name = 'Bill Rideout'
user_email = 'brideout@mit.edu'
user_affiliation = 'MIT'
startDT = datetime.datetime(2019,3,19)
endDT = datetime.datetime(2019,3,19,0, 20)
startLat = 42
endLat = 50
stepLat = 2
startLon = -70
endLon = -68
stepLon = 2
fiveMinSteps = 2
timeSteps = 1
serverUrl = 'localhost'
serverPort = 8123

tecFetcher = skdaccess.geo.tec.binned_tec.stream.DataFetcher(user_name, user_email, user_affiliation, startDT, endDT,
                                           startLat, endLat, stepLat, startLon, endLon, stepLon, 
                                           serverUrl, serverPort,
                                           fiveMinSteps, timeSteps)

for data in tecFetcher:
    print(data[0])
    print(data[1])
    print('Get next')
