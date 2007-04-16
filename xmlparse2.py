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
import xml.etree.ElementTree as ET
import xml.etree.cElementTree as ET
import urllib
import socket

import re
from PyQt4 import QtCore, QtGui

from utilities import *

socket.setdefaulttimeout(5) # timeout in seconds

def parseXMLSkills(inFile):
    etree = ET.parse(inFile)

    root = etree.getroot()
    chars = root.find('characters')
    if chars == None:
        # Yield 1 in case of no <characters> tag
        yield 1
    char = chars.findall('character')
    if char[0].find('skills') != None:
        char = char[0]
    else:
        # Yield 1 in case of error.
        yield 1
    
    skills = char.find('skills')
    for skillGroup in skills.findall('skillGroup'):
        for skill in skillGroup.findall('skill'):
            yield(skill.get('typeName') + '|' + skill.get('typeID') + '|' + skill.find('level').text)

def openConnection(url):
    settings = QtCore.QSettings("Kavanagh Productions", "KMM")
    proxy = str(settings.value("proxy", QtCore.QVariant('')).toString())
    proxies = {'http': proxy}
    try:
        if proxy == '' or proxy == 'http://':
            urlopener = urllib.URLopener()
        else:
            urlopener = urllib.URLopener(proxies)
        xml = urlopener.open(url)
    except Exception, message:
        return 1
    return xml
    

def parseMinsStandardXML(index):
    """
    Grabs the mineral prices from standard EVE-Mon XML
    http://www.phoenix-industries.org - http://www.phoenix-industries.org/evemonprices.xml
    http://eve.battleclinic.com - http://eve.battleclinic.com/eve_online/market.php?feed=xml
    """
    indexes = {'phoenix': 'http://www.phoenix-industries.org/evemonprices.xml',
               'battleclinic': 'http://eve.battleclinic.com/eve_online/market.php?feed=xml',
               'EVE-Central': 'http://eve-central.com/home/marketstat_xml.html?evemon=1'}

    xml = openConnection(indexes[index])
    if xml == 1:
        yield 1     # In case of error
    etree = ET.parse(xml)
    root = etree.getroot()
    mins = root.findall('mineral')
    for min in mins:
        yield(min.find('name').text + '|' + money_me(float(min.find('price').text)))

def parseMinQuant():
    """
    Grabs the mineral prices from Quant Corporation
    http://www.starvingpoet.net/
    """
    urlopener = openConnection('http://www.starvingpoet.net/includes/minerals.php')
    if urlopener == 1:
        yield 1     # In case of error
    xml = urlopener.read()
    regexp = re.compile(r'<TD WIDTH="\d*px">(\w*)</TD><TD WIDTH=.*?>([0-9\.\,]*)</TD><TD.*?>[0-9\.\,]*</TD>')
    m = regexp.findall(xml)
    for i in xrange(8):
        yield(m[i][0] + '|' + m[i][1])
