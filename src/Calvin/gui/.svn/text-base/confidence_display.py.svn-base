"""
confidence_display.py

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

from Calvin.reasoning.confidence import Applic, Validity

__QUALS = [Validity.accept, Validity.sound, Validity.prob, Validity.plaus]
__ApplicES = [Applic.ct, Applic.ft, Applic.dt, Applic.cf, Applic.ff, Applic.df]
__COLORS = [[(45, 85, 60), (65, 125, 90), (110, 190, 140), (170, 230, 190)],
            [(15, 120, 105), (20, 185, 160), (55, 235, 205), (175, 250, 225)],
            [(0, 90, 100), (0, 140, 155), (30, 240, 220), (170, 245, 255)],
            [(130, 70, 5), (200, 110, 5), (250, 170, 80), (255, 210, 160)],
            [(175, 30, 10), (230, 40, 10), (250, 105, 85), (250, 180, 170)],
            [(90, 40, 60), (125, 55, 80), (175, 85, 120), (220, 170, 185)]]


def getIndex(conf):
    """
    Translates a confidence value into a specific row, column
    index (rows are counted from the top down)
    """
    
    if conf is None:
        return None
    
    return (__getApplicIndex(conf.applic), __getValidityIndex(conf.valid))

def __getApplicIndex(app):
    return __ApplicES.index(app)

def __getValidityIndex(val):
    return __QUALS.index(val)

def getColor(confidence):
    """
    Returns the display color (as an RGB tuple) for the passed-
    in confidence value.
    """
    
    index = getIndex(confidence)
    return __COLORS[index[0]][index[1]]
    
    
    