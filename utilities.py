#############################################################################
##
## Copyright (C) 2006-2006 Kavanagh Productions. All rights reserved.
##
## This file is part of the Kavanagh Manufacture Manager - KMM.
## Find more information in: http://kavanaghprod.googlepages.com
## Contact at kavanaghprod@gmail.com
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.gnu.org/licenses/gpl.txt
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
## $Rev$
## $Date$
##
#############################################################################

import sys
import os
import re
import locale
from time import time

from releaseinfo import LIBSDIR
    
def dot_me(amount):
    """
    formats the number to use thousands . separator
    """
    if amount == "": amount = 0
    locale.setlocale(locale.LC_NUMERIC, 'en_US')
    return locale.format("%.0f", amount, 1)

def money_me(amount):
    """
    formats the number to look like money: 1,123.00
    """
    if amount == "": amount = 0
    locale.setlocale(locale.LC_NUMERIC, 'en_US')
    return locale.format("%.2f", amount, 1)

def unmoney_me(amount):
    """
    inverse of money_me()
    """
    if amount == "": amount = 0
    new = re.sub(",", "", str(amount))
    return float(new)

def undot_me(amount):
    """
    removes the dots in thousands - inverse of dot_me() - returns a float
    """
    if amount == "": amount = 0
    new = re.sub(",", "", str(amount))
    new = re.sub("\D", "", str(new))
    return float(new)

def int_undot_me(amount):
    """
    removes the dots in thousands - inverse of dot_me() - returns an int
    """
    if amount == "": amount = 0
    new = re.sub(",", "", str(amount))
    new = re.sub("\D", "", str(new))
    return int(new)

def executable_path():
    """
    return the path of the executable
    """
    if os.path.split(os.path.dirname(sys.argv[0]))[1].endswith(LIBSDIR):
        path = os.path.split(os.path.dirname(sys.argv[0]))[0]
    else:
        path = os.path.dirname(sys.argv[0])
    return path

def calculateMinerals(base, waste, ME, PE, batches):
    """
    Calculates the minerals needed for the production using the characters and BP attributes 
    """
    a = batches*round(base*(waste/(ME+1)))
    b = batches*(base*(0.25-(0.05*int(PE))))
    return int((base*batches) + a + b)

#--------------------- Decorators --------------------------
    
def traced(func):
    def wrapper(*__args,**__kw):
        print "entering", func.__name__
        try:
            return func(*__args,**__kw)
        finally:
            print "exiting", func.__name__
    return wrapper
    
def timethis(func):
    def wrapper(*__args,**__kw):
        start = time()
        try:
            return func(*__args,**__kw)
        finally:
            end = time() - start
            print "Function" , func.__name__ , "took " , end , " seconds."
    return wrapper
    
    
