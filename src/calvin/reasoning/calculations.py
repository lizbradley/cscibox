"""
calculations.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# This module contains all the functions that do various sorts of 
# calculations...
import samples

"""
calcMean
A function that calculates the mean of all fields of the name fName ???
Arguments
fName - A string of the fieldname to find the mean of ???
Returns : A floating point of the mean
"""
def calcMean(fName):
    sum = reduce(lambda x, y: x + y, samples.getAllFlds(fName), 0)
    l = len(samples.sampleList)
    # As not to divide by zero
    if l == 0:
        l = 1
    result = sum / l
    return result
calcMean.userDisp = {'infix':False, 'text':'average'}

"""
calcMax
Calculates the max of a sample
Arguments
fName - The name of the sample
Returns : A floating point of the maximum value
"""
def calcMax(fName):
    return calcMaxSample(fName)[fName]
calcMax.userDisp = {'infix':False, 'text':'maximum value of'}

"""
calcMin
Calculates the min of a sample
Arguments
fName - The name of the sample
Returns : A floating point of the minimum value
"""
def calcMin(fName):
    return calcMinSample(fName)[fName]
calcMin.userDisp = {'infix':False, 'text':'minimum value of'}

"""
calcMaxSample
Calculates the max of a sample
Arguments
fName - The name of the sample
Returns : A sample structure ??? of the max value ???
"""
def calcMaxSample(fName):
    return reduce(lambda x, y: samples.sampleMax(x, y, fName),
                  samples.sampleList)
calcMaxSample.userDisp = {'infix':False, 'text':'sample with maximum'}

"""
calcMinSample
Calculates the min of a sample
Arguments
fName - The name of the sample
Returns : A sample structure ??? of the minimum value ???
"""
def calcMinSample(fName):
    """
    Just like calcMin but returns a sample, not a value.
    """
    return reduce(lambda x, y: samples.sampleMin(x, y, fName),
                  samples.sampleList)
calcMinSample.userDisp = {'infix':False, 'text':'sample with minimum'}

"""
calcDensity
Calculates the sample density of every sample based on how close other
samples are. Sets this as a sample parameter.
It seems that this is not implemented
"""
#TODO
def calcDensity():
    return 0
calcDensity.userDisp = {'infix':False, 'text':'sample density'}
    

