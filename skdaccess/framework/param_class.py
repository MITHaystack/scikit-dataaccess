# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude
# This software has been created in projects supported by the US National
# Science Foundation and NASA (PI: Pankratius)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# """@package AlgoParam
# Provides tunable parameter classes for use in the Computer-Aided Discovery pipeline.
# """


import random
import itertools

class AutoParam:
    '''
    Defines a tunable parameter class inherited by specific subclasses

    AutoParam class and subclass work on a single value.
    functions: perturb value and reset to initial value    
    '''
        
    def __init__(self, val_init):
        '''
        Initialize an AutoParam object.

        @param val_init: Value for parameter
        '''
        self.val        = val_init
        self.val_init   = val_init
        
    def perturb(self):
        '''
        Perturb paramter.

        This class doesn't change the value.
        '''
        self.val = self.val
        
    def reset(self):
        ''' Reset value to initial value '''
        self.val = self.val_init
 
    def __str__(self):
        '''
        String representation of class

        @return String of current value
        '''
        return str(self.val)

    def __call__(self):
        '''
        Retrieves current value of the parameter

        @return Current value of the parameter
        '''
        
        return self.val
        

class AutoParamMinMax(AutoParam):
    '''
    A tunable parameter with min and max ranges, perturbs to a random value in range.

    It can optionally choose either the min or the max after n perturbs
    '''
    
    def __init__(self, val_init, val_min, val_max, decimals=0, extreme=0):
        ''' 
        Construct AutoParamMinMax object

        @param val_init: Initial value for parameter
        @param val_min: Minimum value for param
        @param val_max: Maximum value for parameter
        @param decimals: Number of decimals to include in the random number
        @param extreme: Either the maximum or minimum is chosen every
                        extreme number of iterations. Using a value of
                        one will be an extreme value every time.
                        Using a value of zero will always choose a
                        random value.
        
        '''
        self.val        = val_init
        self.val_init   = val_init        
        self.val_min    = val_min
        self.val_max    = val_max
        self.n = 0
        self.n_max = extreme
        self.decimals = decimals
        
        
    def perturb(self):
        ''' 
        Peturb the paramter by choosing a random value between val_min and val_max. 

        Will choose a random number with precision specified by decimals. Will optionally
        pick the min or the max value after a specified number of perturb calls
        '''

        if self.n == self.n_max - 1:
            # Choose and extreme value
            self.val = random.sample([self.val_min, self.val_max], 1)[0]
            self.n = 0

        else:
            if self.decimals == 0:
                self.val = random.randint(self.val_min,self.val_max)
            else:
                self.val = random.random() * (self.val_max - self.val_min + 10**-self.decimals) + (self.val_min - 0.5 * 10**-self.decimals)
                self.val = round(self.val, ndigits=self.decimals)

            if self.n_max > 0:
                self.n += 1

    def reset(self):
        ''' Reset to initial value '''
        self.n = 0
        self.val = self.val_init
        


class AutoParamList(AutoParam):
    '''
    A tunable parameter with a specified list of choices that can be randomly selected via perturb
    '''
    def __init__(self, val_init, val_list):
        ''' 
        Construct an AutoParamList object

        @param val_init: initial value for the parameter
        @param val_list: List of possible variants for the parameter
        '''
        self.val        = val_init
        self.val_init   = val_init
        self.val_list   = val_list
        
    def perturb(self):
        ''' Randomly select a value from val_list '''
        self.val = random.choice(self.val_list)

    def reset(self):
        ''' Reset the list to the default value '''
        self.val = self.val_init

class AutoParamListCycle(AutoParam):
    '''
    Cycles through a list of paramters
    '''
    def __init__(self, val_list):
        '''
        Construct an AutoParamListCycle

        @param val_list: List of possible variants for the parameter
        '''
        self.val = val_list[0]
        self.val_list = val_list
        self.current_index = 0

    def perturb(self):
        '''
        Select the next value from the list of parameters.
        '''
        if self.current_index >= len(self.val_list) - 1:
            self.current_index = 0
        else:
            self.current_index += 1
            
        self.val = self.val_list[self.current_index]

    def reset(self):
        ''' Reset the list to the default values '''
        self.val = self.val_list[0]
        self.current_index = 0

### Starting list perturber
class AutoList(object):
    '''
    Specifies a list for returning selections of lists, as opposed to a single element
    '''
    def __init__(self, val_list):
        '''
        Construct a AutoList object
        
        @param val_list: List of parameters
        '''
        
        self.val_init   = val_list
        self.val_list   = val_list
 
    def val(self):
        '''
        Retrieves current list of parameters.

        @return List of current parameters 
        '''
        return self.val_list

    def perturb(self):
        ''' This class doesn't change the list when being perturbed '''

        self.val_list = self.val_list
        
    def reset(self):
        ''' Reset current list to initial list '''
        self.val_list = self.val_init

    def getAllOptions(self):
        '''
        Get all possible options

        @return List that contains every option that could possibly be selected
        '''
        return self.val_init
 
    def __str__(self):
        '''
        String representation of class.

        @return String containing all parmaters in list
        '''

        return '[' + ', '.join([str(val) for val in self.val_list]) + ']'
        
        return str(self.val_list)
        
    def __len__(self):
        '''
        Retrieves the length of parameters contained in the list

        @return Number of elements in the list
        '''
        return len(self.val_list)

    def __getitem__(self, ii):
        '''
        Retrieves item from list

        @param ii: Index of item to be retrieved
        @return Item at index ii
        '''
        return self.val_list[ii]

    def __setitem__(self, ii, val):
        ''' 
        Set a value in the list.

        @param ii: Index of list to be set
        @param val: Input value
        '''
        self.val_list[ii] = val
        
    def __call__(self):
        '''
        Retrieve current list

        @return Current list
        '''
        return self.val_list



class AutoListSubset(AutoList):
    '''
    An AutoList perturber that creates random subsets of a list. List can be empty
    '''    
    def perturb(self):
        ''' Peturb the list by selecting a random subset of the initial list '''
        # randomly index list elements to be kept
        index = [random.randint(0,1) for r in range(len(self.val_init))]
        # update list and keep list values where index is 1
        self.val_list = list(itertools.compress(self.val_init, index))



class AutoListPermute(AutoList):
    '''
    A perturber that permutes a list
    '''
    def perturb(self):
        ''' Randomly permutes the initial list '''
        random.shuffle(self.val_list)  #shuffles in place and updates at same time



class AutoListRemove(AutoList):
    '''
    Removes a different single element from the initial list at each perturb call
    '''   
    def __init__(self, val_list):
        ''' 
        Construct a AutoList_Cycle object

        @param val_list: Initial list of parameters.
        '''
        self.n = -1
        super(AutoListRemove, self).__init__(val_list)
        
    def perturb(self):
        ''' 
        Systematically change which item is absent from the list
        '''
        self.n = self.n + 1
        if self.n >= len(self.val_init):
            self.n = 0
        index = [1 for i in range(len(self.val_init))]
        index[self.n] = 0

        self.val_list = list(itertools.compress(self.val_init, index))

    def reset(self):
        ''' Reset the list to its initial value '''
        self.n = -1
        self.val_list = self.val_init
        
class AutoListCycle(AutoList):
    '''
    An Autolist that cycles through different lists
    '''
    def __init__(self, list_val_list):
        '''
        Construct a AutoList_Cycle object

        @param list_val_list: List of different lists to cycle through
        '''

        self.list_val_list = list_val_list
        self.val_list = self.list_val_list[0]
        self.index = 0


    def perturb(self):
        '''
        Select next list from list of lists
        '''
        if self.index < len(self.list_val_list) - 1:
            self.index += 1
        else:
            self.index = 0

        self.val_list = self.list_val_list[self.index]

    def reset(self):
        '''
        Resets to the first list in the list of lists
        '''
        self.index = 0
        self.val_list = self.list_val_list[self.index]

    def getAllOptions(self):
        '''
        Get elements that could possibly be called

        @return List of all possible elements
        '''
        
        all_options = []
        for option_list in list_val_list:
            all_options += option_list

        return all_options
