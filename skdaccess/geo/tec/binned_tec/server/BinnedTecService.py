"""BinnedTecService.py is an Xmlrpc service that creates and caches Binned TEC data.  

In particular, this service allows a certain number of session.  For each service, it returns binned TEC data,
and then creates the next request in anticipation of the next request, until the last bin in requested.

This version does not need to run on Madrigal, since it is uses madrigalWeb to get data

$Id: BinnedTecService.py 15171 2019-06-12 18:25:59Z brideout $
"""

# standard python imports
import os, sys, os.path
import io
import argparse
import xmlrpc.server
import threading
import datetime, time
import tempfile

# third party imports
import numpy
import pandas

# Madrigal imports
import madrigalWeb.madrigalWeb



class BinnedTecData(object):
    """BinnedTecObject is the object that contains data about a single binned tec session
    """
    def __init__(self, user_name, user_email, user_affiliation, startDT, endDT,
                 startLat, endLat, stepLat, startLon, endLon, stepLon,
                 fiveMinSteps, timeSteps):
        """__init__ creates a new BinnedTecData object
        
        Inputs:
        
        @param user_name: user name (string)
        @param user_email: user email (string)
        @param user_affiliation: user affiliation (string)
        @param startDT - datetime.datetime to start data collection
        @param endDT - datetime.datetime to end iteration
        @param startLat - lower latitude to start at (-90 to 90, integer)
        @param endLat - upper latitude to end at (-90 to 90, integer)
        @param stepLat - latitude step (minimum 1, integer, (endLat - startLat) % stepLat must == 0)
        @param startLon - lower longitude to start at (-90 to 90, integer)
        @param endLon - upper longitude to end at (-90 to 90, integer)
        @param stepLon - longitude step (minimum 1, integer, (endLon - startLon) % stepLon must == 0)
        @param fiveMinSteps: number of 5 minutes steps to median filter over (min=1, integer)
        @param timeSteps: number of time periods to increment each time. 1 is continuous data. (min=1, integer)
        
        Returns: None
        
        Affects: creates a new BinnedTecData object.  All input arguments are class variables.
        Also creates self.lastDT, which keeps track of iteration, and self.cachedData, where cachedData is
        a pandas data frame where the 2D data is vertical TEC, the row indices are the latitudes, and the columns are the
        longitudes, unless this is last item in iterator, in which case cachedData is None.  If cachedData is being updated,
        cachedData is ''.  Also creates self.cachedDT, which is datetime of start of cached data.  Finally, creates
        self.updateDT, which simply tracks the last time updateCache called. This is used to remove stale cached data.
        """
        # set class variables and error check
        
        # user_name
        if not isinstance(user_name, str):
            raise ValueError('user_name argument not a string, type = %s' % (str(type(user_name))))
        if len(user_name) == 0:
            raise ValueError('user_name argument cannot be zero length')
        self.user_name = user_name
        
        # user_email
        if not isinstance(user_email, str):
            raise ValueError('user_email argument not a string, type = %s' % (str(type(user_email))))
        if len(user_email) == 0:
            raise ValueError('user_email argument cannot be zero length')
        if user_email.find('@') == -1:
            raise ValueError('user_email argument must contain @ character')
        self.user_email = user_email
        
        # user_affiliation
        if not isinstance(user_affiliation, str):
            raise ValueError('user_affiliation argument not a string, type = %s' % (str(type(user_affiliation))))
        if len(user_affiliation) == 0:
            raise ValueError('user_affiliation argument cannot be zero length')
        self.user_affiliation = user_affiliation
        
        # startDT
        if not isinstance(startDT, datetime.datetime):
            raise ValueError('startDT argument not a datetime, type = %s' % (str(type(startDT))))
        self.startDT = startDT
        self.lastDT = startDT # state variable
        
        # endDT
        if not isinstance(endDT, datetime.datetime):
            raise ValueError('endDT argument not a datetime, type = %s' % (str(type(endDT))))
        if endDT < startDT:
            raise ValueError('endDT argument must be greater than startDT')
        self.endDT = endDT
        
        # startLat
        if not isinstance(startLat, int):
            raise ValueError('startLat argument not a int, type = %s' % (str(type(startLat))))
        if startLat < -90 or startLat > 90:
            raise ValueError('startLat argument must be -90 to 90')
        self.startLat = startLat
        
        # endLat
        if not isinstance(endLat, int):
            raise ValueError('endLat argument not a int, type = %s' % (str(type(endLat))))
        if endLat < -90 or endLat > 90:
            raise ValueError('endLat argument must be -90 to 90')
        if endLat <= startLat:
            raise ValueError('endLat argument must be greater than startLat')
        self.endLat = endLat
        
        # stepLat
        if not isinstance(stepLat, int):
            raise ValueError('stepLat argument not a int, type = %s' % (str(type(stepLat))))
        if stepLat < 1:
            raise ValueError('stepLat argument must be 1 or greater')
        if (endLat - startLat) % stepLat != 0:
            raise ValueError('(endLat - startLat) % stepLat must == 0')
        self.stepLat = stepLat
        
        # startLon
        if not isinstance(startLon, int):
            raise ValueError('startLon argument not a int, type = %s' % (str(type(startLon))))
        if startLon < -180 or startLon > 180:
            raise ValueError('startLon argument must be -180 to 180')
        self.startLon = startLon
        
        # endLon
        if not isinstance(endLon, int):
            raise ValueError('endLon argument not a int, type = %s' % (str(type(endLon))))
        if endLon < -180 or endLon > 180:
            raise ValueError('endLon argument must be -180 to 180')
        if endLon <= startLon:
            raise ValueError('endLon argument must be greater than startLon')
        self.endLon = endLon
        
        # stepLon
        if not isinstance(stepLon, int):
            raise ValueError('stepLon argument not a int, type = %s' % (str(type(stepLon))))
        if stepLon < 1:
            raise ValueError('stepLon argument must be 1 or greater')
        if (endLon - startLon) % stepLon != 0:
            raise ValueError('(endLon - startLon) % stepLon must == 0')
        self.stepLon = stepLon
        
        # fiveMinSteps
        if not isinstance(fiveMinSteps, int):
            raise ValueError('fiveMinSteps argument not a int, type = %s' % (str(type(fiveMinSteps))))
        if fiveMinSteps < 1:
            raise ValueError('fiveMinSteps argument must be 1 or greater')
        self.fiveMinSteps = fiveMinSteps
        
        # timeSteps
        if not isinstance(timeSteps, int):
            raise ValueError('timeSteps argument not a int, type = %s' % (str(type(timeSteps))))
        if timeSteps < 1:
            raise ValueError('timeSteps argument must be 1 or greater')
        self.timeSteps = timeSteps
        
        self.madWeb = madrigalWeb.madrigalWeb.MadrigalData('http://cedar.openmadrigal.org')
        
        self.fullData = self.getFullData()
        
        self.cachedData = ''
        
        self.updateCache()
        
        
    def getFullData(self):
        """getFullData returns a string representing all data needed for the iteration
        """
        sDT = self.startDT
        eDT = self.endDT
        
        exps = self.madWeb.getExperiments(8000, sDT.year, sDT.month, sDT.day, sDT.hour, sDT.minute, sDT.second, 
                                          eDT.year, eDT.month, eDT.day, eDT.hour, eDT.minute, eDT.second)
        
        exps.sort()
        
        # if no experiments, no data
        if len(exps) == 0:
            return('')
        
        fileList = []
        for exp in exps:
            time.sleep(1)
            files = self.madWeb.getExperimentFiles(exp.id)
            for f in files:
                if f.kindat != 3500:
                    continue
                fileList.append(f.name)
                break
        if len(fileList) != len(exps):
            raise ValueError('Not all TEC experiments had binned data')
        
        # create time filters
        filter = ' date1=%s time1=%s date2=%s time2=%s ' % (sDT.strftime('%m/%d/%Y'), sDT.strftime('%H:%M:%S'),
                                                            eDT.strftime('%m/%d/%Y'), eDT.strftime('%H:%M:%S'))
        # add lat, lon filters
        filter += ' filter=gdlat,%i,%i ' % (self.startLat, self.endLat)
        filter += ' filter=glon,%i,%i ' % (self.startLon, self.endLon)
        
        parms = 'year,month,day,hour,min,sec,gdlat,glon,tec'
        
        # build result string
        resultStr = ''
        for f in fileList:
            result= self.madWeb.isprint(f, parms, filter, self.user_name, self.user_email, self.user_affiliation)
            if result.find('No records') == -1:
                resultStr += result
                
        return(resultStr)
        
        
    def updateCache(self):
        """updateCache either sets cachedData to a pandas object, or sets it to None if iterator ends
        """
        if self.cachedData is None:
            return # already done
        
        sDT = self.lastDT
        eDT = sDT + datetime.timedelta(minutes = int(5 *self.fiveMinSteps))
        self.cachedDT = sDT
        self.updateDT = datetime.datetime.utcnow()
        
        # reset self.lastDT
        self.lastDT += datetime.timedelta(minutes = int(5 *self.fiveMinSteps * self.timeSteps))
        
        if sDT >= self.endDT:
            self.cachedData = None
            return
                
        self.cachedData = self.filterData(sDT, eDT)
            
            
    
    def filterData(self, sDT, eDT):
        """filterData takes the filters lines from self.fullData to create pandas DataFrame,
        or None if no data
        
        """
        # create a dictionary with key = (lat int, lon int), value = list of tec values
        dataDict = {}
        for lat in range(0, int((self.endLat - self.startLat) // self.stepLat) + 1):
            for lon in range(0, int((self.endLon - self.startLon) // self.stepLon) + 1):
                dataDict[(lat, lon)] = []

        lines = self.fullData.split('\n')
        dataFound = False 
        for line in lines:
            items = line.split()
            if len(items) < 9:
                continue
            year = int(items[0])
            month = int(items[1])
            day = int(items[2])
            hour = int(items[3])
            minute = int(items[4])
            second = int(float(items[5]))
            thisDT = datetime.datetime(year, month, day, hour, minute, second)
            if thisDT < sDT:
                continue
            if thisDT > eDT:
                break
            ilat = int(float(items[6]))
            ilon = int(float(items[7]))
            latKey = int((ilat - self.startLat) // self.stepLat)
            lonKey = int((ilon - self.startLon) // self.stepLon)
            dataDict[(latKey, lonKey)].append(float(items[8]))
            dataFound = True
            
        if not dataFound:
            return(None) # no more data
            
            
        tecData = numpy.full((int((self.endLat - self.startLat) // self.stepLat) + 1,
                              int((self.endLon - self.startLon) // self.stepLon) + 1),
                             fill_value=numpy.nan, dtype=numpy.float64)
        for latKey, lonKey in dataDict.keys():
            if len(dataDict[(latKey, lonKey)]) > 0:
                tecData[latKey, lonKey] = numpy.median(numpy.array(dataDict[(latKey, lonKey)]))
            
        # final step to be done - convert into pandas
        latIndices = numpy.arange(self.startLat, self.endLat + self.stepLat, self.stepLat)
        lonColumns = numpy.arange(self.startLon, self.endLon + self.stepLon, self.stepLon)
        
        pandasTec = pandas.DataFrame(data=tecData, index=latIndices, columns=lonColumns)
        
        return(pandasTec)
    
    
    
class BinnedTecCache(object):
    """BinnedTecCache is the main cache of BinnedTecObjects that are updated by BinnedTecUpdater
    """
    def __init__(self):
        """__init__ creates self.cacheDict, which is a dictionary of keys = id (int), value = BinnedTecObject 
        """
        self.cacheDict = {}
        self.cacheTimeOut = datetime.timedelta(hours=1)
        
    def addTecData(self, user_name, user_email, user_affiliation, startDT, endDT,
             startLat, endLat, stepLat, startLon, endLon, stepLon,
             fiveMinSteps, timeSteps):
        """addTecData creates a new key in self.cacheDict, with key = lowest available non-negitive integer in
        self.cacheDict.keys(), and value = BinnedTecData object
        
        Inputs:
        
            @param user_name: user name (string)
            @param user_email: user email (string)
            @param user_affiliation: user affiliation (string)
            @param startDT - datetime.datetime to start data collection
            @param endDT - datetime.datetime to end iteration
            @param startLat - lower latitude to start at (-90 to 90, integer)
            @param endLat - upper latitude to end at (-90 to 90, integer)
            @param stepLat - latitude step (minimum 1, integer, (endLat - startLat) % stepLat must == 0)
            @param startLon - lower longitude to start at (-90 to 90, integer)
            @param endLon - upper longitude to end at (-90 to 90, integer)
            @param stepLon - longitude step (minimum 1, integer, (endLon - startLon) % stepLon must == 0)
            @param fiveMinSteps: number of 5 minutes steps to median filter over (min=1, integer)
            @param timeSteps: number of time periods to increment each time. 1 is continuous data. (min=1, integer)
        
        Returns: key for this BinnedTecObject in self.cacheDict
        """
        key = 1
        while key in self.cacheDict.keys():
            key += 1
            
        binnedTecObj = BinnedTecData(user_name, user_email, user_affiliation, startDT, endDT,
                                     startLat, endLat, stepLat, startLon, endLon, stepLon,
                                     fiveMinSteps, timeSteps)
        self.cacheDict[key] = binnedTecObj
        
        return(key)
    
    
    def pop(self, key):
        """pop returns the next object in the form of a tuple of (datetime, binary pickled pandas object).  Returns
        None if no key or iteration complete
        """
        if not key in self.cacheDict:
            return(None)
        while(isinstance(self.cacheDict[key].cachedData, str)):
            time.sleep(3)  # waiting for cache update
            continue
        
        if self.cacheDict[key].cachedData is None:
            return(None)
        
        # pickle pandas data
        f = tempfile.NamedTemporaryFile()
        self.cacheDict[key].cachedData.to_pickle(f.name)
        pickledData = f.read()
        f.close()
        dt = self.cacheDict[key].cachedDT
        # let the thread know an update is needed
        self.cacheDict[key].cachedData = ''
        return((dt, pickledData))
        
        
    def update(self):
        """update loops through all keys in self.cacheDict.  If BinnedTecData.cachedData == '', calls 
        BinnedTecData.updateCache.  Else if BinnedTecData.updateDT more than self.cacheTimeOut old, deletes key and value
        """
        keys = self.cacheDict.keys()
        keysToDelete = []
        for key in keys:
            binnedTecObj = self.cacheDict[key]
            if isinstance(binnedTecObj.cachedData, str):
                binnedTecObj.updateCache()
            elif datetime.datetime.utcnow() - binnedTecObj.updateDT > self.cacheTimeOut:
                keysToDelete.append(key)
                
        for key in keysToDelete:
            del self.cacheDict[key]
            
        
        
            
            
class BinnedTecUpdater(threading.Thread):
    def __init__(self, binnedTecCache, exitEvent):
        """__init__ sets up the BinnedTecUpdater thread
        
        Inputs:
        
            @param binnedTecCache - a BinnedTecCache to keep updated
            @param exitEvent - threading.Event() object to indicate shut down
        """
        threading.Thread.__init__(self)
        
        self.binnedTecCache = binnedTecCache
        self.exitEvent = exitEvent
        
        
    def run(self):
        while not exitEvent.isSet():
            self.binnedTecCache.update()
            time.sleep(1)
            
            
class BinnedTecService:
    """BinnedTecService provides the xml-rpc interface to this service
    """
    def __init__(self, binnedTecCache, exitEvent):
        """__init__ sets up the BinnedTecService
        
        Inputs:
        
            @param binnedTecCache - a BinnedTecCache to interact with
            @param exitEvent - threading.Event() object to indicate shut down
        """
        self.binnedTecCache = binnedTecCache
        self.exitEvent = exitEvent
        
        
    def create(self, user_name, user_email, user_affiliation, startDT, endDT,
             startLat, endLat, stepLat, startLon, endLon, stepLon,
             fiveMinSteps, timeSteps):
        """creates creates a new iterator over binned TEC data.  Returns a key as an identifier.
        
        Inputs:
        
            @param user_name: user name (string)
            @param user_email: user email (string)
            @param user_affiliation: user affiliation (string)
            @param startDT - datetime.datetime to start data collection
            @param endDT - datetime.datetime to end iteration
            @param startLat - lower latitude to start at (-90 to 90, integer)
            @param endLat - upper latitude to end at (-90 to 90, integer)
            @param stepLat - latitude step (minimum 1, integer, (endLat - startLat) % stepLat must == 0)
            @param startLon - lower longitude to start at (-90 to 90, integer)
            @param endLon - upper longitude to end at (-90 to 90, integer)
            @param stepLon - longitude step (minimum 1, integer, (endLon - startLon) % stepLon must == 0)
            @param fiveMinSteps: number of 5 minutes steps to median filter over (min=1, integer)
            @param timeSteps: number of time periods to increment each time. 1 is continuous data. (min=1, integer)
        
        Returns: key for iterator
        """
        key = self.binnedTecCache.addTecData(user_name, user_email, user_affiliation, startDT, endDT,
                                             startLat, endLat, stepLat, startLon, endLon, stepLon,
                                             fiveMinSteps, timeSteps)
        return(key)
        
        
    def next(self, key):
        """next returns the next object in the form of a tuple of (datetime, binary pickled pandas object).  Returns
        None in key not found, or if no more data.
        """
        data = self.binnedTecCache.pop(key)
        return(data)
            
            
            
# main begins here - main runs xmlrpc service
if __name__ == '__main__':
    
    usage = 'python BinnedTecService.py [port]  (default part 8123)'
    port = 8123
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            print(usage)
            sys.exit(-1)
    
    # create object to be shared by main thread and BinnedTecUpdated
    binnedTecCache = BinnedTecCache()
    
    exitEvent = threading.Event()
    
    # start up the thread that will constantly update binnedTecCache
    binnedTecUpdate = BinnedTecUpdater(binnedTecCache, exitEvent)
    binnedTecUpdate.start()
    
    # Create server
    with xmlrpc.server.SimpleXMLRPCServer(('localhost', port), allow_none=True, use_builtin_types=True) as server:
        server.register_introspection_functions()
        server.register_instance(BinnedTecService(binnedTecCache, exitEvent))
        
        # Run the server's main loop
        server.serve_forever()
    
    
            
    
    
        
    
        
        
        
        
        