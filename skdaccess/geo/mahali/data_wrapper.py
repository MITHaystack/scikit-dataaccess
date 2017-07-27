from skdaccess.framework.data_class import DataWrapperBase

class DataWrapper(DataWrapperBase):
    '''Data wrapper for Mahali data'''
    def getIterator(self):
        ''' 
        Get iterator to Mahali data

        @return Iterator yielding (site,date,nav,obs)
        '''
        for item in self.data:
            yield item[0], item[1], item[2], item[3]
