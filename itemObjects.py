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
#############################################################################

from PyQt4 import QtCore, QtGui

from dbUtils import KMMdatabase
from utilities import *


class itemObject(object):
    def __init__(self, ID, typeID, quantity, date, pe, BPme, BPpe, loc, status):

        self.ID             = ID
        self.typeID         = typeID
        self.itemQuantity   = quantity
        self.date           = date
        self.pe             = pe
        self.BPme           = BPme
        self.BPpe           = BPpe
        self.locationID     = str(loc)
        self.statusID       = status

        try:
            self.KMMdatabase = KMMdatabase('KMM')
            self.EVEdatabase = KMMdatabase('EVE')
        except Exception:
            print str(val)
            sys.exit(-1)

        self.getAdditionalData()

    def getAdditionalData(self):
        loc = self.KMMdatabase.queryData('''
            SELECT location
            FROM locations
            WHERE ID = ?;''', (str(self.locationID),))
        self.location = loc[0][0]

        stat = self.KMMdatabase.queryData('''
            SELECT status
            FROM productionStatus
            WHERE ID = ?;''', (str(self.statusID),))
        self.status = stat[0][0]

        item = self.EVEdatabase.queryData('''
            SELECT item.typename, bp.productiontime
            FROM invTypes item, invBlueprintTypes bp
            WHERE bp.productTypeID = item.typeID
            AND item.typeID = ?;''', (str(self.typeID),))
        self.itemName = str(item[0][0])
        self.prodtime = str(item[0][1])

    def getKMMDatabaseData(self):
        """
        Returns the raw data to be inserted in KMM database
        """
        return ((self.typeID,self.itemQuantity,self.date,self.pe,self.BPme, self.BPpe,self.locationID,self.statusID))

    def getTableData(self):
        tableData = [self.ID, self.itemName, self.itemQuantity, self.status, 
                     self.date, self.pe, self.BPme,self.BPpe, self.location]
        matTypeID = (34, 35, 36, 37, 38, 39, 40, 11399)
        self.totalCost = 0

        bpData = self.EVEdatabase.queryData('''
            SELECT  mat.typeID, mat.typename, comp_mat.quantity,
                    mat.groupID, bp.wastefactor
            FROM invBlueprintTypes bp, invtypes mat, TL2MaterialsForTypeWithActivity comp_mat,
                 invTypes bpitem, invTypes item
            WHERE bp.productTypeID = ?
            AND item.typeID = bp.productTypeID
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            ORDER BY mat.typeID;''',(str(self.typeID),) )

        materialQuant = {}

        for matID, matName, quantity, groupID, waste in bpData:
            self.waste = float(waste)/100

            if groupID == 18:    # Only minerals
                materialQuant[matID] = quantity
                
        for m in matTypeID:
            if m not in materialQuant:
                materialQuant[m] = 0

        for matID in materialQuant.iterkeys():
            quantity = materialQuant[matID]
            self.totalCost += (self.calculatePrice(quantity, matID))[0]
            tableData.append(calculateMinerals(quantity, self.waste, self.BPme, self.pe, self.itemQuantity))

        tableData.insert(4,money_me(self.totalCost))

        # This method returns a tuple consisting of:
        #    (ID-lot, itemName, itemQuantity, status, cost
        #     date, pe, BPme, BPpe, location,
        #     trit, pye, mex, iso, nocx, zyd, mega, morph)
        return (tableData)

    def calculatePrice(self, quantity, mineralID):
        cost = self.KMMdatabase.queryData('''
            SELECT cost, quantity 
            FROM mineral_stock
            WHERE ID = ?;''', (str(mineralID),))
        mineralcost  = cost[0][0]
        mineralStock = cost[0][1]
        mineralPrice = calculateMinerals(quantity, self.waste, self.BPme, self.pe, self.itemQuantity)*mineralcost
        return (mineralPrice, mineralStock)

class buildStatusCombo(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.KMMdatabase = KMMdatabase('KMM')
        statuses = self.KMMdatabase.queryData('''
            SELECT ID, status 
            FROM productionstatus;
            ''')
        for ID, status in statuses:
            self.addItem(status, QtCore.QVariant(ID))
        self.show()