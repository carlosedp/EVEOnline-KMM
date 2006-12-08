from dbUtils import KMMdatabase
from utilities import *
from PyQt4 import QtCore, QtGui

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
        except Exception, val:
#            QtGui.QMessageBox.critical( self, 'Fatal Error'), str(val), 
#                QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
            print str(val)
            sys.exit(-1)

        self.getAdditionalData()
        self.getItemName()

    def getKMMDatabaseData(self):
        """
        Returns the raw data to be inserted in KMM database
        """
        return ((self.typeID,self.itemQuantity,self.date,self.pe,self.BPme, self.BPpe,self.locationID,self.statusID))

    def getAdditionalData(self):
        loc = self.KMMdatabase.queryData('''
            SELECT location
            FROM locations
            WHERE ID = ''' + str(self.locationID) + ';')
        self.location = loc[0][0]
        stat = self.KMMdatabase.queryData('''
            SELECT status
            FROM productionStatus
            WHERE ID = ''' + str(self.statusID) + ';')
        self.status = stat[0][0]

    def getItemName(self):
        item = self.EVEdatabase.queryData('''
            SELECT typename
            FROM invTypes
            WHERE typeID = ''' + str(self.typeID) + ';')
        self.itemName = str(item[0][0])
    	

    def getTableData(self):
        tableData = [self.ID, self.itemName, self.itemQuantity, self.status, 
                     self.date, self.pe, self.BPme,self.BPpe, self.location]
        matTypeID = (34, 35, 36, 37, 38, 39, 40, 11399)
        self.totalCost = 0

        bpData = self.EVEdatabase.queryData('''
            SELECT  mat.typeID, mat.typename, comp_mat.quantity,
                    mat.groupID, bp.wastefactor, bp.productiontime
            FROM invBlueprintTypes bp, invtypes mat, TL2MaterialsForTypeWithActivity comp_mat,
                 invTypes bpitem, invTypes item
            WHERE bp.productTypeID = ''' + str(self.typeID) + '''
            AND item.typeID = bp.productTypeID
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            ORDER BY mat.typeID;''')

        materialQuant = {}

        for matID, matName, quantity, groupID, waste, prodtime in bpData:
            self.waste = float(waste)/100
            self.prodtime = prodtime

            if groupID == 18:    # Only minerals
                materialQuant[matID] = quantity
                
        for m in matTypeID:
            if not materialQuant.has_key(m):
                materialQuant[m] = 0
        	
        for matID in materialQuant.iterkeys():
            quantity        = materialQuant[matID]
            self.totalCost  += (self.calculatePrice(quantity, matID))[0]
            tableData.append(calculateMinerals(quantity, self.waste, self.BPme, self.pe, 1))

        tableData.insert(4,money_me(self.totalCost))
        return (tableData)

    def calculatePrice(self, quantity, mineralID):
        cost = self.KMMdatabase.queryData('''
            SELECT cost, quantity 
            FROM mineral_stock
            WHERE ID = ''' + str(mineralID) + ';')
        mineralcost  = cost[0][0]
        mineralStock = cost[0][1]
        mineralPrice = calculateMinerals(quantity, self.waste, self.BPme, self.pe, self.itemQuantity)*mineralcost
        return (mineralPrice, mineralStock)

	