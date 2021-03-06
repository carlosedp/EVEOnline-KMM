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
        except DatabaseException:
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
            SELECT item.typename, bp.productiontime, cat.categoryID, cat.categoryName
            FROM invTypes item, invBlueprintTypes bp, invCategories cat, invGroups grp
            WHERE bp.productTypeID = item.typeID
            AND item.groupID = grp.groupID
            AND grp.categoryID = cat.categoryID
            AND item.typeID = ?;''', (str(self.typeID),))
        self.itemName = str(item[0][0])
        self.prodtime = str(item[0][1])
        self.categoryID = str(item[0][2])
        self.categoryName = str(item[0][3])
        
    def getKMMDatabaseData(self):
        """
        Returns the raw data to be inserted in KMM database
        """
        return ((self.typeID,self.itemQuantity,self.date,self.pe,self.BPme, self.BPpe,self.locationID,self.statusID))

    def getItemData(self):
        tableData = [self.ID, self.itemName, self.itemQuantity, self.status, 
                     self.date, self.pe, self.BPme,self.BPpe, self.location]
        return tableData
                     
    def getMaterials(self):
        tableData = [self.ID, self.itemName, self.itemQuantity, self.status, 
                     self.date, self.pe, self.BPme,self.BPpe, self.location]
        self.totalCost = 0

        bpData = self.EVEdatabase.queryData('''
            SELECT  mat.typeID, mat.typename, comp_mat.quantity, comp_mat.damagePerJob,
                    mat.groupID, bp.wastefactor, grp.groupName, grp.categoryID, cat.categoryName
               FROM invBlueprintTypes bp, invtypes mat, TL2MaterialsForTypeWithActivity comp_mat,
                    invTypes bpitem, invTypes item, invGroups grp, invcategories cat
               WHERE bp.productTypeID = ?
               AND mat.groupID = grp.groupID
               AND grp.categoryID = cat.categoryID
               AND item.typeID = bp.productTypeID
               AND bp.blueprinttypeID = bpitem.typeID
               AND bpitem.typeID = comp_mat.typeID
               AND mat.typeID = comp_mat.requiredTypeID
               AND comp_mat.activity = 1
               ORDER BY mat.typeID;''',(str(self.typeID),) )
        self.minerals = {}
        self.modules = {}
        self.commodities = {}
        self.skills = {}
        
        for matID, matName, quantity, damage, groupID, waste, groupName ,catID, catName in bpData:

            if groupID == 18:    # Minerals
                self.minerals[matID] = {'name': matName,
                                        'quantity': quantity,
                                        'waste': float(waste)/100,
                                        'groupname': groupName
                                        }
            elif catID == 7:    # Modules
                #self.categoryID
                pass
            elif catID == 17:   # Commodity
                #self.categoryID
                pass
            elif catID == 16:   # Skill
                pass
                                        
        mineralName = ("Tritanium","Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", "Megacyte", "Morphite")
        mineralID = (34, 35, 36, 37, 38, 39, 40, 11399)
        
        for mID,mName in zip(mineralID,mineralName):
            if mID not in self.minerals:
                 self.minerals[mID] = {'name': mName,
                                       'quantity': 0,
                                       'waste': 0,
                                       'groupname': "Mineral"
                                       }
        for min in self.minerals:
            self.minerals[min]['quantity'] = (calculateMinerals(self.minerals[min]['quantity'], 
                                                                self.minerals[min]['waste'], 
                                                                self.BPme, 
                                                                self.pe, 
                                                                self.itemQuantity))
        # Minerals calculated at this point
        return (self.minerals,)

    def getItemCost(self):
        """
        This function receives a tuple with:
        (minerals, modules, commodities)
        """
        totalCost = 0
        try: 
            self.minerals
        except AttributeError:
            self.getMaterials()
        for mineral in self.minerals:                                      
            self.totalCost += (self.calculatePrice(self.minerals[mineral]['quantity'],
                                                   self.minerals[mineral]['waste'], 
                                                   mineral))[0]
        return money_me(self.totalCost)

    def calculatePrice(self, quantity, waste ,mineralID):
        cost = self.KMMdatabase.queryData('''
            SELECT cost, quantity 
            FROM mineral_stock
            WHERE ID = ?;''', (str(mineralID),))
        mineralcost  = cost[0][0]
        mineralStock = cost[0][1]
        mineralPrice = quantity*mineralcost
        return (mineralPrice, mineralStock)

class buildStatusCombo(QtGui.QComboBox):
    """
    This class is used in capital ships window to display the status combobox inside the table.
    """
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