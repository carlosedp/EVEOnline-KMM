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

from utilities import *
from dbUtils import KMMdatabase, DatabaseException
from itemObjects import *
from xmlparse2 import *

from UI.ui_minstock import Ui_MineralStock
from UI.ui_production import Ui_Production
from UI.ui_production_hist import Ui_ProductionHist
from UI.ui_skills import Ui_CharacterSkills
from UI.ui_addchar import Ui_addCharacter
from UI.ui_assets import Ui_Assets
from UI.ui_capitalships import Ui_CapitalShips
from UI.ui_sales import Ui_Sales
from UI.ui_configproxy import Ui_ConfigProxy


class internalWindows(QtGui.QMainWindow):
    """ 
    This is the base class for all child windows
    """
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)
        self.name = self.objectName()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        # Create two database instances
        try:
            self.KMMdatabase = KMMdatabase('KMM')
            self.EVEdatabase = KMMdatabase('EVE')
        except DatabaseException, val:
            QtGui.QMessageBox.critical( self, self.tr('Fatal Error'), str(val),
                                        QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
            sys.exit(-1)

    def closeEvent(self, event):
        # Executed when the user closes the window
        windowName = self.parent.openwindowsInstances[self]
        self.parent.openwindowsInstances.__delitem__(self)
        self.parent.openwindowsNames.__delitem__(windowName)
        try:
            self.KMMdatabase.closeDatabase()
            self.EVEdatabase.closeDatabase()
        except DatabaseException, val:
            QtGui.QMessageBox.critical( self, self.tr('Fatal Error'), str(val),
                                        QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
        event.accept()


class minStockWindow(internalWindows,Ui_MineralStock):
    """
    Mineral stock and prices window
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.stockISK    = 0
        self.costFields  = (None, self.triCost,self.pyeCost,self.mexCost, self.isoCost, 
                            self.nocCost, self.zydCost, self.megCost, self.morCost)
        self.ISKFields   = (None, self.triISK,self.pyeISK,self.mexISK, self.isoISK,
                            self.nocISK, self.zydISK, self.megISK, self.morISK)
        self.quantFields = (None, self.triQuant,self.pyeQuant,self.mexQuant, self.isoQuant,
                            self.nocQuant, self.zydQuant, self.megQuant, self.morQuant)

        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.populateValues)
        self.connect(self.saveButton, QtCore.SIGNAL("clicked()"),self.saveValues)
        
        self.connect(self.actionConfigure_Proxy, QtCore.SIGNAL("triggered()"), self.configProxy)
        self.connect(self.actionPhoenix_Industries, QtCore.SIGNAL("triggered()"), self.updatePhoenix)
        self.connect(self.actionQuant_Corporation, QtCore.SIGNAL("triggered()"), self.updateQuant)
        self.connect(self.actionBattleclinic, QtCore.SIGNAL("triggered()"), self.updateBattleclinic)
        self.connect(self.actionEVE_Central, QtCore.SIGNAL("triggered()"), self.updateEVECentral)


        self.populateValues()

    def populateValues(self):
        self.stockISK = 0
        data = self.KMMdatabase.queryData('''
            SELECT fieldID, quantity, IFNULL(cost,0) 
            FROM mineral_stock;
            ''')
        for ID, qt, cost in data:
                self.updFields(ID, qt, cost)
        self.totalISK.setText(money_me(self.stockISK))

    def updFields(self, ID, qt, cost):
        self.quantFields[ID].setText(dot_me(qt))
        self.costFields[ID].setText(money_me(cost))
        self.ISKFields[ID].setText(money_me(cost*qt))
        self.stockISK += cost * qt

    def saveValues(self):
        for ID in range(1, len(self.quantFields)):
            self.updDatabase(ID)
        self.KMMdatabase.commitData()
        self.populateValues()
        try:
            self.parent.openwindowsNames[assetsWindow].loadAll()
            self.parent.openwindowsNames[productionWindow].updateFields()
        except KeyError:
            pass

    def updDatabase(self, ID):
        quant = self.quantFields[ID].text()
        if quant[0] == '+':
            quant = 'quantity+' + str(int(quant[1:]))
        elif quant[0] == '-':
            quant = 'quantity-' + str(int(quant[1:]))
        else:
            quant = undot_me(quant)
            
        cost = self.costFields[ID].text()
        self.KMMdatabase.updateData('''
            UPDATE OR REPLACE mineral_stock 
            SET quantity = ''' + str(quant) + ''', 
            cost = ? 
            WHERE fieldID = ? ;''', (unmoney_me(cost), ID))

    def updateQuant(self):
        self.updateStandardXMLSource(parseMinQuant())

    def updatePhoenix(self):
        self.updateStandardXMLSource(parseMinsStandardXML('phoenix'))

    def updateBattleclinic(self):
        self.updateStandardXMLSource(parseMinsStandardXML('battleclinic'))

    def updateEVECentral(self):
        self.updateStandardXMLSource(parseMinsStandardXML('EVE-Central'))

    def updateStandardXMLSource(self, source):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        for line in source:
            data = line.split("|")
            min = str(data[0])
            price = str(data[1])
            if min == 'Tritanium': self.triCost.setText(price); continue
            if min == 'Pyerite': self.pyeCost.setText(price); continue
            if min == 'Mexallon': self.mexCost.setText(price); continue
            if min == 'Isogen': self.isoCost.setText(price); continue
            if min == 'Nocxium': self.nocCost.setText(price); continue
            if min == 'Zydrine': self.zydCost.setText(price); continue
            if min == 'Megacyte': self.megCost.setText(price); continue
            if min == 'Morphite': self.morCost.setText(price); continue

        QtGui.QApplication.restoreOverrideCursor()
        self.parent.statusbar.showMessage("Prices updated, save to use these indexes for you calculation.",5000)        
        self.statusbar.showMessage("Prices updated, save to use these indexes for you calculation.")
        
    def configProxy(self):
        self.parent.openWindow(configureProxy)

class configureProxy(internalWindows, Ui_ConfigProxy):
    """
    Window to change proxy configuration
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.connect(self.addButton, QtCore.SIGNAL("clicked()"),self.save)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.closeWindow)
        
        settings = QtCore.QSettings("Kavanagh Productions", "KMM")
        proxy = settings.value("proxy", QtCore.QVariant('http://')).toString()
        if proxy == '': proxy = 'http://'
        self.address.setText(proxy)
        
    def closeWindow(self):
        self.close()

    def save(self):
        address = str(self.address.text())
        settings = QtCore.QSettings("Kavanagh Productions", "KMM")
        settings.setValue("proxy", QtCore.QVariant(address))
        
        self.close()
        
class productionWindow(internalWindows,Ui_Production):
    """
    Manages the items manufacturing
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        # Runs all functions to populate and update window fields
        self.populateStatusCombo()
        self.populateItemCombo()
        self.populateLocationCombo()
        self.populateFilterCombo()
        self.setupTable()
        self.getSkills()
        self.updateFields()
        self.itemID.hide()
        self.date.setText(QtCore.QDate.currentDate().toString("dd/MM/yyyy"))

        # Creates all signals to widgets
        self.connect(self.itemCombo, QtCore.SIGNAL("currentIndexChanged(int)"),self.itemSelected)
        self.connect(self.quantitySpin, QtCore.SIGNAL("valueChanged(int)"),self.quantityChanged)
        self.connect(self.PeSkill, QtCore.SIGNAL("textChanged(QString)"),self.PeChanged)
        self.connect(self.BpMe, QtCore.SIGNAL("textChanged(QString)"),self.MeChanged)
        self.connect(self.BpPe, QtCore.SIGNAL("textChanged(QString)"),self.PeChanged)
        self.connect(self.insertButton, QtCore.SIGNAL("clicked()"),self.insertJob)
        self.connect(self.updateButton, QtCore.SIGNAL("clicked()"),self.updateJob)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"),self.deleteJob)
        self.connect(self.viewFilteredButton, QtCore.SIGNAL("clicked()"),self.viewFiltered)
        self.connect(self.prodTable, QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"),self.loadToEdit)
        self.connect(self.locationCombo, QtCore.SIGNAL("activated(int)"),self.locationComboLoad)        
        self.connect(self.yourBPs, QtCore.SIGNAL("stateChanged(int)"),self.onlyUserBPs)        
        self.connect(self.deleteLocationButton, QtCore.SIGNAL("clicked()"),self.deleteLocation)
        self.connect(self.exportButton, QtCore.SIGNAL("clicked()"),self.exportCSVData)

    def populateStatusCombo(self):
        statuses = self.KMMdatabase.queryData('''
            SELECT ID, status 
            FROM productionstatus;
            ''')
        for ID, status in statuses:
            self.buildStatusCombo.addItem(status, QtCore.QVariant(ID))

    def populateItemCombo(self, type=0):
        """
        Implement T2 items one day...
        type = 0 - Load all BPs
        type = 2 - Load only BPs from user Assets
        """
        self.itemCombo.clear()
        if type == 0:
            items = self.EVEdatabase.queryData('''
                SELECT module.typename "Module", module.typeID "typeID"
                FROM invTypes module, invBlueprintTypes bp, invTypes bpitem
                WHERE bp.productTypeID = module.typeID
                AND bp.blueprinttypeID = bpitem.typeID
                AND (module.typeid NOT IN
                      (SELECT typeid FROM invmetatypes WHERE
                       metaGroupID != 1))
                AND NOT (
                        module.typename LIKE '% test %'
                     OR module.typename LIKE 'test%'
                     OR module.typename LIKE '%test'
                     OR module.typename LIKE '%meta%'
                     OR module.typename LIKE '%test'
                     OR module.typename LIKE '% old'
                     OR module.typename LIKE '%unused'
                     OR module.typename LIKE '%tier%'
                     OR module.typename LIKE '"%'
                     OR module.typename LIKE "'%"
                     )
                ORDER BY module.typename;
                ''')
        elif type == 2:
            userBPs = self.KMMdatabase.queryData('''
                SELECT DISTINCT(productTypeID)
                FROM BPAssets
                WHERE (BPType = 'BPC' AND runs > 0) OR (BPType = 'BPO');
                ''')
            userBP = []
            [userBP.append(x[0]) for x in userBPs]
            userBP = repr(tuple(userBP))
            items = self.EVEdatabase.queryData('''
                SELECT module.typename "Module", module.typeID "typeID"
                FROM invTypes module, invBlueprintTypes bp, invTypes bpitem
                WHERE bp.productTypeID = module.typeID
                AND bp.blueprinttypeID = bpitem.typeID
                AND (module.typeid NOT IN
                      (SELECT typeid FROM invmetatypes WHERE
                       metaGroupID != 1))
                AND NOT (
                        module.typename LIKE '% test %'
                     OR module.typename LIKE 'test%'
                     OR module.typename LIKE '%test'
                     OR module.typename LIKE '%meta%'
                     OR module.typename LIKE '%test'
                     OR module.typename LIKE '% old'
                     OR module.typename LIKE '%unused'
                     OR module.typename LIKE '%tier%'
                     OR module.typename LIKE '"%'
                     OR module.typename LIKE "'%"
                     )
               AND module.typeID IN ''' + userBP + '''
               ORDER BY module.typename;
               ''')
        for module, ID in items:
            self.itemCombo.addItem(module, QtCore.QVariant(ID))

    def populateFilterCombo(self):
        self.filterNames = ['Default', 'Planned','Pre-Production','Building', 'Delivered']
        self.filters     = [' statusID in (1,2,3,4)',' statusID like 1',
                            ' statusID like 2',' statusID like 3',' statusID like 4']
        for filter in self.filterNames:
            self.filterCombo.addItem(filter) 

    def populateLocationCombo(self):
        self.locationCombo.clear()
        locations = self.KMMdatabase.queryData('''
                SELECT ID, location 
                FROM locations;
                ''')
        for ID, location in locations:
            self.locationCombo.addItem(location, QtCore.QVariant(ID)) 

    def deleteLocation(self):
        loc = str(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        result = QtGui.QMessageBox.question( self, self.tr('Remove location'), 
                    self.tr("Do you want to delete the selected location from the database?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 16384:
            items = self.KMMdatabase.queryData('''
                SELECT ID 
                FROM itemmanufacture
                WHERE locationID = ?
                OR sale_locationID = ?;''', (loc, loc))
            if items != []:
                QtGui.QMessageBox.critical( self, self.tr('Items on database'), "You currently have items using this location. Update your items to delete this.",
                                            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
                return
            else:
                count = self.KMMdatabase.queryData('''
                            select count(1) FROM locations;''')
                if count[0][0] <= 1:
                    QtGui.QMessageBox.critical( self, self.tr('Delete location'), "You need at least one location in database. Add a new one to delete this.",
                                                QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
                    return
                self.KMMdatabase.queryData('''
                    DELETE FROM locations
                    WHERE ID = ?;''', (loc,))
                self.KMMdatabase.commitData()
        self.populateLocationCombo()

    def locationComboLoad(self):
        typedLocation = str(self.locationCombo.currentText())
        loc = []
        locations = self.KMMdatabase.queryData('''
            SELECT location 
            FROM locations;
            ''')
        for location in locations:
            loc.append(location[0])
        if typedLocation not in loc:
            result = QtGui.QMessageBox.question( self, self.tr('Add location'), 
                        self.tr("The location you typed do not exists in database, add it?"),
                        QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
            if result == 16384:
                self.KMMdatabase.updateData('''
                    INSERT INTO locations (location) 
                    VALUES (?);
                    ''', (typedLocation,))
                self.KMMdatabase.commitData()
                self.populateLocationCombo()
            else:
                self.populateLocationCombo()
        
    def getSkills(self):
        skill = self.KMMdatabase.queryData('''
            SELECT skilllevel 
            FROM characterskills 
            WHERE skillID = 3388 
            AND charID = ?;''', (self.parent.activeChar[0],))
        try:
            self.PeSkill.setText(str(skill[0][0]))
        except IndexError:
            QtGui.QMessageBox.critical( self, self.tr('Error'),"No active character found. Go to Skills window and set an active char.",
                            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)


    def onlyUserBPs(self, status):
        self.disconnect(self.itemCombo, QtCore.SIGNAL("currentIndexChanged(int)"),self.itemSelected)
        self.populateItemCombo(status)
        self.connect(self.itemCombo, QtCore.SIGNAL("currentIndexChanged(int)"),self.itemSelected)
        self.itemSelected()

    def insertJob(self):
        typeID      = int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString())
        quantity    = int(self.quantitySpin.value())
        date        = str(self.date.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        locationID  = int(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        statusID    = int(self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString())

        Item = itemObject(None, typeID, quantity, date, pe, BPme, BPpe, locationID, statusID)

        if statusID == 3: #Only for items entered in "Build" status.
            if self.decreaseMinsBPs(Item, typeID):
                self.KMMdatabase.updateData('''
                    INSERT INTO itemmanufacture 
                    (typeID, quantity, date, pe, BPme, BPpe, locationID, statusID) 
                    VALUES (?,?,?,?,?,?,?,?);
                    ''', Item.getKMMDatabaseData())

                self.KMMdatabase.commitData()
                self.setupTable()

        else:
            self.KMMdatabase.updateData('''
                INSERT INTO itemmanufacture 
                (typeID, quantity, date, pe, BPme, BPpe, locationID, statusID) 
                VALUES (?,?,?,?,?,?,?,?);
                ''', Item.getKMMDatabaseData())

            self.KMMdatabase.commitData()
            self.setupTable()
        try:
            self.parent.openwindowsNames[assetsWindow].loadAll()
            self.parent.openwindowsNames[minStockWindow].populateValues()
        except KeyError:
            pass

    def updateJob(self):
        if not self.itemID.text():
            return
        ID          = int(self.itemID.text())
        typeID      = int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString())
        quantity    = int(self.quantitySpin.value())
        date        = str(self.date.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        locationID  = int(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        statusID    = int(self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString())

        itemData = (typeID, quantity, date, pe, BPme, BPpe, locationID, statusID, ID)

        Item = itemObject(None, typeID, quantity, date, pe, BPme, BPpe, locationID, statusID)

        if statusID == 3: #Only for items entered in "Build" status.
            if self.decreaseMinsBPs(Item, typeID):
                self.KMMdatabase.updateData('''
                    UPDATE itemmanufacture 
                    SET typeID = ?, quantity = ?, date = ?, pe = ?, 
                        BPme = ?, BPpe = ?, locationID = ?, statusID = ?
                    WHERE ID = ?;
                    ''', itemData)
                note = str(self.itemNotes.toPlainText())
                self.KMMdatabase.updateData('''
                    INSERT OR REPLACE INTO constructionNotes (constID, note) 
                    VALUES (?, ?);''', (ID, note))
                self.KMMdatabase.commitData()
                self.setupTable()
        else:
            self.KMMdatabase.updateData('''
                UPDATE itemmanufacture 
                SET typeID = ?, quantity = ?, date = ?, pe = ?, 
                    BPme = ?, BPpe = ?, locationID = ?, statusID = ?
                WHERE ID = ?;
                ''', itemData)
            note = str(self.itemNotes.toPlainText())
            self.KMMdatabase.updateData('''
                INSERT OR REPLACE INTO constructionNotes (constID, note) 
                VALUES (?, ?);''', (ID, note))

            self.KMMdatabase.commitData()
            self.setupTable()

        try:
            self.parent.openwindowsNames[productionHistWindow].setupTable()
            self.parent.openwindowsNames[assetsWindow].loadAll()
            self.parent.openwindowsNames[minStockWindow].populateValues()
        except KeyError:
            pass

    def decreaseMinsBPs(self, Item, typeID):
        result = QtGui.QMessageBox.question( self, self.tr('Enter production'), 
                    self.tr("This job production will start, substract the minerals and BPCs run from your stock and assets?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)

        if result == 16384: #Yes
            try: #Minerals
                minerals = [34, 35, 36, 37, 38, 39, 40, 11399]
                itemquant = Item.itemQuantity
                itemMinerals = Item.getMaterials()[0]
                
                mineralData = self.KMMdatabase.queryData('''
                    SELECT ID, quantity 
                    FROM mineral_stock;
                    ''')
                
                for mineral, stock in zip(minerals, mineralData):
                    if mineral == stock[0]:
                        if itemMinerals[mineral]['quantity'] <= stock[1]:
                            newStock = stock[1]-(itemMinerals[mineral]['quantity'])
                            self.KMMdatabase.updateData('''
                                UPDATE mineral_stock 
                                SET quantity = ?
                                WHERE ID = ?;
                                ''',(newStock, mineral))
                        else:
                            raise Exception(itemMinerals[mineral]['name'])
            
            except Exception, mineral:
                message = 'You dont have enought ' + str(mineral) + '. Job not added.'
                QtGui.QMessageBox.critical( self, self.tr('Error'),message,
                                            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
                self.KMMdatabase.rollbackData()
                return 0

            try: #Blueprints
                BpData = self.KMMdatabase.queryData('''
                    SELECT bptype, runs, ID
                    FROM BPAssets
                    WHERE (BPType = 'BPC' AND runs > 0) OR (BPType = 'BPO')
                    AND productTypeID = ?
                    ORDER BY BPType DESC;
                ''', (str(typeID),))

                if BpData == []:
                    raise Exception
                bp = BpData[0]
                if bp[0] == 'BPO':
                    pass
                elif bp[0] == 'BPC' and bp[1] >= itemquant:
                    newRuns = bp[1]-itemquant
                    self.KMMdatabase.updateData('''
                        UPDATE BPAssets 
                        SET runs = ?
                        WHERE ID = ?;
                        ''',(newRuns, bp[2]))
                elif bp[0] == 'BPC' and bp[1] < itemquant:
                    raise Exception

            except:
                message = 'You dont have a blueprint for this item or no runs left in your BPC'
                QtGui.QMessageBox.critical( self, self.tr('Error'),message,
                                            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
                self.KMMdatabase.rollbackData()
                return 0
                
            self.KMMdatabase.commitData()
        return 1

    def deleteJob(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected job from the database?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)

        if result == 16384:
            #Yes
            items = []
            for item in self.prodTable.selectedRanges():
                if item.rowCount() == 1:
                    items.append(item.topRow())
                elif item.rowCount() >1:
                    for i in range(item.topRow(), item.bottomRow()+1):
                        items.append(i)

            for row in items:
                ID = str(self.prodTable.item(row,0).text())
                self.KMMdatabase.updateData('''
                    DELETE FROM itemmanufacture 
                    WHERE ID = ?;
                    ''', (ID,))
                self.KMMdatabase.updateData('''
                    DELETE FROM constructionnotes
                    WHERE constID = ?;
                    ''', (ID,))
            self.KMMdatabase.commitData()
        self.setupTable()

    def loadToEdit(self):
        row = self.prodTable.currentRow()

        self.itemCombo.setCurrentIndex(self.itemCombo.findText(self.prodTable.item(row,1).text()))
        self.quantitySpin.setValue(int(self.prodTable.item(row,2).text()))
        self.date.setText(self.prodTable.item(row,5).text())
        self.PeSkill.setText(self.prodTable.item(row,6).text())
        self.BpMe.setText(self.prodTable.item(row,7).text())
        self.BpPe.setText(self.prodTable.item(row,8).text())
        self.locationCombo.setCurrentIndex(self.locationCombo.findText(self.prodTable.item(row,9).text()))
        self.buildStatusCombo.setCurrentIndex(self.buildStatusCombo.findText(self.prodTable.item(row,3).text()))
        self.itemID.setText(self.prodTable.item(row,0).text())

        #self.updateFields()    # Check if the loading fails in prodWindow

        ID = str(self.prodTable.item(row,0).text())
        try:
            note = self.KMMdatabase.queryData('''
                SELECT note from constructionNotes
                WHERE constID = ?;''', (ID,))
            note = str(note[0][0])
            self.itemNotes.setPlainText(note)
        except IndexError:
            self.itemNotes.setPlainText("")

    def viewFiltered(self):
        self.setupTable(self.filterNames[self.filterCombo.currentIndex()])
    
    def setupTable(self, filtertype="Default"):
        # Sets the table
        self.prodTable.setSortingEnabled(False)
        for row in range(self.prodTable.rowCount()):
            self.prodTable.removeRow(0)
        self.prodTable.verticalHeader().hide()

        tableColumns = ["Lot ID.", "Item", "Quantity", "Status","Total Cost", 
                        "Date", "PE", "BP ME", "BP PE",  "Location", "Tritanium",
                        "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
                        "Megacyte", "Morphite"]
        self.prodTable.setColumnCount(len(tableColumns))
        self.prodTable.setHorizontalHeaderLabels(tableColumns)

        prodItems = self.KMMdatabase.queryData('''
            SELECT ID, typeID, quantity, date, PE, BPME, BPPE, locationID, statusID
            FROM itemmanufacture 
            WHERE capitalship != 1
            AND ''' + self.filters[self.filterNames.index(filtertype)] + ';')
        if prodItems == []:
            return
        for prodItem in prodItems:
            row = self.prodTable.rowCount()
            self.prodTable.insertRow(row)

            Item = itemObject(prodItem[0],prodItem[1],prodItem[2],prodItem[3],
                              prodItem[4],prodItem[5],prodItem[6],prodItem[7],
                              prodItem[8])

            itemMat = Item.getMaterials()[0]
            itemData = Item.getItemData() + [itemMat[mt]['quantity'] for mt in itemMat]
            itemData.insert(4,Item.getItemCost())
            
            for data, col in zip(itemData, range(self.prodTable.columnCount())):
                self.prodTable.setItem(row, col, QtGui.QTableWidgetItem(str(data)))
        
        self.prodTable.setSortingEnabled(True)
        self.prodTable.sortItems(0)
        self.prodTable.resizeColumnsToContents()
        self.prodTable.resizeRowsToContents()

    def itemSelected(self):
        if self.itemCombo.currentIndex() != -1:
            BPme, BPpe = self.getBpMePe(int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString()))
            self.BpMe.setText(str(BPme))
            self.BpPe.setText(str(BPpe))
            self.updateFields()

    def quantityChanged(self):
        self.updateFields()

    def PeChanged(self):
        self.updateFields()

    def MeChanged(self):
        self.updateFields()

    def updateFields(self):
        if (self.PeSkill.text() == "") or (self.BpMe.text() == ""):
            return
        typeID      = int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString())
        quantity    = int(self.quantitySpin.value())
        date        = str(self.date.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        locationID  = str(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        statusID    = self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString()

        Item = itemObject(None, typeID, quantity, date, pe, BPme, BPpe, locationID, statusID)

        matFormFieldsTotal = (self.triTotal, self.pyeTotal, self.mexTotal,
                              self.isoTotal, self.nocTotal, self.zydTotal,
                              self.megTotal, self.morTotal) 
        matFormFieldsEach  = (self.triEach, self.pyeEach, self.mexEach,
                              self.isoEach, self.nocEach, self.zydEach,
                              self.megEach, self.morEach) 
        matTypeID = (34, 35, 36, 37, 38, 39, 40, 11399)
           
        itemData = self.EVEdatabase.queryData('''
            SELECT mat.typeID, comp_mat.quantity, mat.groupID
            FROM invBlueprintTypes bp, invtypes mat, TL2MaterialsForTypeWithActivity comp_mat,
                 invTypes bpitem
            WHERE bp.productTypeID = ?
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            ORDER BY mat.typeID;''', (str(typeID),))

        itemMat = Item.getMaterials()[0]
        materials = [itemMat[mt]['quantity'] for mt in itemMat]

        costEach = 0
        minCost = {}
        minStock = {}

        minCosts = self.KMMdatabase.queryData('''
            SELECT ID, cost, quantity 
            FROM mineral_stock 
            ORDER BY ID;''')

        for min_ID, min_cost, min_stock in minCosts:
            minCost[min_ID]  = min_cost
            minStock[min_ID] = min_stock
        quantity = 1 if quantity ==0 else quantity
                
        for matQuantity, i in zip(materials, range(len(matFormFieldsTotal))):
            
            matFormFieldsTotal[i].setText(dot_me(matQuantity))
            matFormFieldsEach[i].setText(dot_me(matQuantity/quantity))
            costEach += matQuantity*minCost[matTypeID[i]]
            
            if (matQuantity*quantity) > minStock[matTypeID[i]]:
               matFormFieldsTotal[i].setText("<font color='red'>" + matFormFieldsTotal[i].text() + "</font>")
            
        self.costEach.setText(money_me(costEach/quantity))
        self.costTotal.setText(money_me(costEach))

    def getBpMePe(self, itemID):
        data = self.KMMdatabase.queryData('''
            SELECT me, pe 
            FROM BPassets 
            WHERE productTypeID = ?
            ORDER BY me;''', (str(itemID),))
        if data == []:
            return (0,0)
        else:
            return (data[0][0], data[0][1])

    def exportCSVData(self):
        filePath = QtGui.QFileDialog.getSaveFileName(self, self.tr("Create File"),
            "", self.tr("Any (*.*)"))
        if not filePath: 
            return

        f = open(filePath,'w')
        f.write(";".join(("Lot ID.", "Item", "Quantity", "Status","Total Cost", 
                "Date", "PE", "BP ME", "BP PE",  "Location", "Tritanium",
                "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
                "Megacyte", "Morphite")))
        f.write('\n')
        rows = self.prodTable.rowCount()
        cols =  self.prodTable.columnCount()
        for row in xrange(rows):
            for col in xrange(cols):
                f.write(self.prodTable.item(row, col).text()+';')
            f.write('\n')
        f.close()
        msg = 'Your data has been exported successfully. Your file is in: ' + str(filePath)
        QtGui.QMessageBox.information( self, self.tr('Export Sucessful'), 
            self.tr(msg),
            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)


class addCharWindow(internalWindows, Ui_addCharacter):
    """
    Small window to add a new character
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.connect(self.addButton, QtCore.SIGNAL("clicked()"),self.addChar)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.closeWindow)

    def closeWindow(self):
        self.close()

    def addChar(self):
        name    = str(self.charName.text())
        race    = str(self.charRace.text())
        blood   = str(self.charBlood.text())

        self.KMMdatabase.updateData('''
            INSERT INTO characters (name, race, bloodline) 
            VALUES (?,?,?);
            ''', (name, race, blood))
        self.KMMdatabase.commitData()
        self.parent.openwindowsNames[skillsWindow].populateChars()

        self.close()


class skillsWindow(internalWindows,Ui_CharacterSkills):
    """
    Manages the character skills
    Can import the skills from EVE-Online XML file via xmlparse2.py
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.connect(self.addCharButton, QtCore.SIGNAL("clicked()"),self.addCharWindow)
        self.connect(self.delCharButton, QtCore.SIGNAL("clicked()"),self.delChar)
        self.connect(self.makeActiveButton, QtCore.SIGNAL("clicked()"),self.makeActive)
        self.connect(self.saveButton, QtCore.SIGNAL("clicked()"),self.saveSkills)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.loadSkills)
        self.connect(self.importXMLButton, QtCore.SIGNAL("clicked()"),self.importXML)
        self.connect(self.characterCombo, QtCore.SIGNAL("currentIndexChanged(int)"),self.loadSkills)

        self.skillFields = [self.pe,self.industry,self.refining,self.refeff,
                            self.accounting,self.brokerrel,self.science,self.research,self.metallurgy,
                            self.frigconst,self.cruiserconst,self.indconst,self.veld,self.scor,
                            self.pyro,self.plag,self.ombe,self.kern,self.jasp,self.hemo,self.hedb,
                            self.gnei,self.dark,self.spod,self.crok,self.bist,self.arko,self.merc,
                            self.scrapmetal,self.ice]
        self.skillID    = [3388,3380,3385,3389,16622,3446,3402,3403,3409,3395,3397,3396,
                           12195,12193,12192,12191,12190,12188,12187,12186,12185,12184,
                           12183,12194,12182,12181,12180,12189,12196,18025]
        self.populateChars()
        self.characterCombo.setCurrentIndex(self.characterCombo.findData(QtCore.QVariant(parent.activeChar[0])))
        self.loadSkills()


    def importXML(self):
        importedData = {}
        filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
            "", self.tr("XML files (*.xml)"))
        if not filePath: 
            return
        
        for line in parseXMLSkills(str(filePath)):
            if line == 1:
                QtGui.QMessageBox.critical( self, self.tr('Import Error'), 
                    self.tr('Your XML file is invalid. Try downloading it again from EVE-Online website.'),
                    QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
                return 0
            data = line.split("|")
            ID = int(data[1])
            level = int(data[2])
            importedData[ID] = level

        for field in self.skillID:
            if field in importedData:
                self.skillFields[self.skillID.index(field)].setText(str(importedData[field]))
            else:
                self.skillFields[self.skillID.index(field)].setText("0")
                
        QtGui.QMessageBox.information( self, self.tr('Import Sucessful'), 
            self.tr('Your file has been imported successfully, review your skills and save your data using the \'Save\' button.'),
            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
        

    def populateChars(self):
        self.characterCombo.clear()
        data = self.KMMdatabase.queryData('''
            SELECT ID, name
            FROM characters;
            ''')
        if data != []:
            for ID, name in data:
                self.characterCombo.addItem(name, QtCore.QVariant(ID)) 

    def loadSkills(self):
        self.charID = str(self.characterCombo.itemData(self.characterCombo.currentIndex()).toString())
        try:
            levels = self.KMMdatabase.queryData('''
                SELECT skillID, skillLevel 
                FROM characterskills
                WHERE charID = ?;''', (self.charID,))
            for ID, level in levels:
                self.skillFields[self.skillID.index(ID)].setText(str(level))
        except IndexError:
            pass

    def addCharWindow(self):
        self.parent.openWindow(addCharWindow)

    def makeActive(self):
        charID = int(self.characterCombo.itemData(self.characterCombo.currentIndex()).toString())
        charName = str(self.characterCombo.currentText())
        self.parent.activeChar = (charID, charName)
        self.parent.status1.setText("Active Char: " + charName + "  ")
        self.saveSkills()

    def delChar(self):
        self.charID = str(self.characterCombo.itemData(self.characterCombo.currentIndex()).toString())
        result = QtGui.QMessageBox.question( self, self.tr('Remove character'), 
            self.tr("Do you want to delete the selected character?"),
            QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)

        if result == 16384:
            if int(self.charID) == 0:
                QtGui.QMessageBox.information( self, self.tr('Not permitted'), 
                    self.tr('You cannot delete the default character.'),
                    QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
                self.populateChars()
                return
        else:
            return

        self.KMMdatabase.updateData('''
            DELETE FROM characterskills 
            WHERE charID = ?
            ''', (self.charID,))

        self.KMMdatabase.updateData('''
            DELETE FROM characters
            WHERE ID = ?
            ''', (self.charID,))

        self.KMMdatabase.commitData()
        self.populateChars()
        self.characterCombo.setCurrentIndex(self.characterCombo.findText('Default'))
        self.makeActive()

    def saveSkills(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.KMMdatabase.updateData('''
            DELETE FROM characterskills 
            WHERE charID = ?
            ''', (self.charID,))
        for field, skillID in zip(self.skillFields, self.skillID):
            self.updSkillsDB((self.charID, skillID, str(field.text())))
        
        self.KMMdatabase.commitData()
        QtGui.QApplication.restoreOverrideCursor()

    def updSkillsDB(self, values):
        self.KMMdatabase.updateData('''
            INSERT INTO characterskills (charID, skillID, skilllevel) 
            VALUES (?, ?, ?);
            ''' , values)


class productionHistWindow(internalWindows,Ui_ProductionHist):
    """
    Manages the items manufacturing history
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.populateStatusCombo()
        self.populateFilterCombo()
        self.setupTable()
        self.itemID.hide()

        self.connect(self.updateButton, QtCore.SIGNAL("clicked()"),self.updateJob)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"),self.deleteJob)
        self.connect(self.viewFilteredButton, QtCore.SIGNAL("clicked()"),self.viewFiltered)
        self.connect(self.prodTable, QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"),self.loadToEdit)
        self.connect(self.exportButton, QtCore.SIGNAL("clicked()"),self.exportCSVData)

    def updateJob(self):
        ID          = int(self.itemID.text())
        quantity    = int(self.quantity.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        date        = str(self.date.text())
        statusID    = int(self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString())

        itemData = (quantity, date, pe, BPme, BPpe, statusID, ID)

        self.KMMdatabase.updateData('''
            UPDATE itemmanufacture 
            SET quantity = ?, date = ?, pe = ?, BPme = ?, 
                BPpe = ?, statusID = ?
            WHERE ID = ?;
            ''', itemData)

        note = str(self.itemNotes.toPlainText())
        self.KMMdatabase.updateData('''INSERT OR REPLACE INTO constructionNotes
            (constID, note) VALUES (?, ?);''', (ID, note))


        self.KMMdatabase.commitData()
        self.setupTable()
        try:
            self.parent.openwindowsNames[productionWindow].setupTable()
            self.parent.openwindowsNames[assetsWindow].loadAll()
        except KeyError:
            pass
     
    def deleteJob(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected job from the database?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 16384:
            #Yes
            items = []
            for item in self.prodTable.selectedRanges():
                if item.rowCount() == 1:
                    items.append(item.topRow())
                elif item.rowCount() >1:
                    for i in range(item.topRow(), item.bottomRow()+1):
                        items.append(i)

            for row in items:
                ID = str(self.prodTable.item(row,0).text())
                self.KMMdatabase.updateData('''
                    DELETE FROM itemmanufacture 
                    WHERE ID = ?;
                    ''', (ID,))
                self.KMMdatabase.updateData('''
                    DELETE FROM constructionnotes
                    WHERE constID = ?;
                    ''', (ID,))
            self.KMMdatabase.commitData()
        self.setupTable()
 
    def viewFiltered(self):
        self.setupTable(self.filterNames[self.filterCombo.currentIndex()])
        
    def loadToEdit(self):
        row = self.prodTable.currentRow()

        self.itemID.setText(self.prodTable.item(row,0).text())
        self.editItem.setText(self.prodTable.item(row,1).text())
        self.quantity.setText(str(self.prodTable.item(row,2).text()))
        self.buildStatusCombo.setCurrentIndex(self.buildStatusCombo.findText(self.prodTable.item(row,3).text()))
        self.date.setText(self.prodTable.item(row,5).text())
        self.PeSkill.setText(self.prodTable.item(row,6).text())
        self.BpMe.setText(self.prodTable.item(row,7).text())
        self.BpPe.setText(self.prodTable.item(row,8).text())
        self.location.setText(self.prodTable.item(row,9).text())

        self.updateFields()
        ID = str(self.prodTable.item(row,0).text())
        try:
            note = self.KMMdatabase.queryData('''
                SELECT note from constructionNotes
                WHERE constID = ?;''', (ID,))
            note = str(note[0][0])
            self.itemNotes.setPlainText(note)
        except IndexError:
            self.itemNotes.setPlainText("")
     
    def setupTable(self, filtertype="Default"):
        # Sets the table
        self.prodTable.setSortingEnabled(False)
        for row in range(self.prodTable.rowCount()):
            self.prodTable.removeRow(0)
        self.prodTable.verticalHeader().hide()

        tableColumns = ["Lot ID.", "Item", "Quantity", "Status","Total Cost", 
                        "Date", "PE", "BP ME", "BP PE",  "Location", "Tritanium",
                        "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
                        "Megacyte", "Morphite"]
        self.prodTable.setColumnCount(len(tableColumns))
        self.prodTable.setHorizontalHeaderLabels(tableColumns)

        prodItems = self.KMMdatabase.queryData('''
            SELECT ID, typeID, quantity, date, 
                   PE, BPME, BPPE, locationID, statusID
            FROM itemmanufacture 
            WHERE capitalship != 1
            AND ''' + self.filters[self.filterNames.index(filtertype)] + ';')
            
        if prodItems == []:
            return
        for prodItem in prodItems:
            row = self.prodTable.rowCount()
            self.prodTable.insertRow(row)

            Item = itemObject(prodItem[0],prodItem[1],prodItem[2],prodItem[3],
                              prodItem[4],prodItem[5],prodItem[6],prodItem[7],
                              prodItem[8])

            itemMat = Item.getMaterials()[0]
            itemData = Item.getItemData() + [itemMat[mt]['quantity'] for mt in itemMat]
            itemData.insert(4,Item.getItemCost())
            
            for data, col in zip(itemData, range(self.prodTable.columnCount())):
                self.prodTable.setItem(row, col, QtGui.QTableWidgetItem(str(data)))

        self.prodTable.setSortingEnabled(True)
        self.prodTable.sortItems(0)
        self.prodTable.resizeColumnsToContents()
        self.prodTable.resizeRowsToContents()

    def populateFilterCombo(self):
        self.filterNames = ['Default', 'Built','On-Sale','Sold']
        self.filters     = [' statusID in (5,6,7)',' statusID like 5',
                            ' statusID like 6',' statusID like 7']
        for filter in self.filterNames:
            self.filterCombo.addItem(filter) 

    def populateStatusCombo(self):
        statuses = self.KMMdatabase.queryData('''
            SELECT ID, status 
            FROM productionstatus;
            ''')
        for ID, status in statuses:
            self.buildStatusCombo.addItem(status, QtCore.QVariant(ID))

    def updateFields(self):
        if (self.PeSkill.text() == "") or (self.BpMe.text() == ""):
            return
        
        typeID = self.EVEdatabase.queryData('''
            SELECT typeID FROM invTypes
            WHERE typeName LIKE ?;''', (str(self.editItem.text()),))
        typeID = typeID[0][0]

        date        = str(self.date.text())
        quantity    = int(self.quantity.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())

        Item = itemObject(None, typeID, quantity, date, pe, BPme, BPpe, 1, 1)

        matFormFieldsTotal = (self.triTotal, self.pyeTotal, self.mexTotal,
                              self.isoTotal, self.nocTotal, self.zydTotal,
                              self.megTotal, self.morTotal) 
        matFormFieldsEach  = (self.triEach, self.pyeEach, self.mexEach,
                              self.isoEach, self.nocEach, self.zydEach,
                              self.megEach, self.morEach) 
        matTypeID = (34, 35, 36, 37, 38, 39, 40, 11399)
           
        itemData = self.EVEdatabase.queryData('''
            SELECT mat.typeID, comp_mat.quantity, mat.groupID
            FROM invBlueprintTypes bp, invtypes mat, TL2MaterialsForTypeWithActivity comp_mat,
                 invTypes bpitem
            WHERE bp.productTypeID = ?
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            ORDER BY mat.typeID;
            ''', (str(typeID),))

        itemMat = Item.getMaterials()[0]
        materials = [itemMat[mt]['quantity'] for mt in itemMat]
        costTotal  = 0

        minCost  = {}
        minStock = {}
        minCosts = self.KMMdatabase.queryData('''
            SELECT ID, cost, quantity 
            FROM mineral_stock 
            ORDER BY ID;
            ''')

        for min_ID, min_cost, min_stock in minCosts:
            minCost[min_ID] = min_cost
            minStock[min_ID] = min_stock

        quantity = 1 if quantity ==0 else quantity
        for matQuantity, i in zip(materials, range(len(matFormFieldsTotal))):
            matFormFieldsTotal[i].setText(dot_me(matQuantity))
            matFormFieldsEach[i].setText(dot_me(matQuantity/quantity))
            costTotal += matQuantity*minCost[matTypeID[i]]
            if (matQuantity*quantity) > minStock[matTypeID[i]]:
               matFormFieldsTotal[i].setText("<font color='red'>" + matFormFieldsTotal[i].text() + "</font>")
            
        self.costEach.setText(money_me(costTotal/quantity))
        self.costTotal.setText(money_me(costTotal))

    def exportCSVData(self):
        filePath = QtGui.QFileDialog.getSaveFileName(self, self.tr("Create File"),
            "", self.tr("Any (*.*)"))
        if not filePath: 
            return

        f = open(filePath,'w')
        f.write(";".join(("Lot ID.", "Item", "Quantity", "Status","Total Cost", 
                "Date", "PE", "BP ME", "BP PE",  "Location", "Tritanium",
                "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
                "Megacyte", "Morphite")))
        f.write('\n')
        rows = self.prodTable.rowCount()
        cols =  self.prodTable.columnCount()
        for row in xrange(rows):
            for col in xrange(cols):
                f.write(self.prodTable.item(row, col).text()+';')
            f.write('\n')
        f.close()
        msg = 'Your data has been exported successfully. Your file is in: ' + str(filePath)
        QtGui.QMessageBox.information( self, self.tr('Export Sucessful'), 
            self.tr(msg),
            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)

        
        
class assetsWindow(internalWindows,Ui_Assets):
    """
    Assets management window
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.loadAll()
        self.setCombos()

        self.connect(self.addButton, QtCore.SIGNAL("clicked()"),self.addBP)
        self.connect(self.delButton, QtCore.SIGNAL("clicked()"),self.delBP)
        self.connect(self.updButton, QtCore.SIGNAL("clicked()"),self.updBP)
        self.connect(self.BPtable, QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"),self.loadToEdit)

    def loadAll(self):
        self.loadMinerals()
        self.loadItems()
        self.loadBluePrints()
        total = self.mineralISKTotal + self.itemsISKTotal + self.bpISKTotal
        self.total.setText(money_me(total))

    def addBP(self):
        productID = self.itemCombo.itemData(self.itemCombo.currentIndex()).toInt()[0]
        productName = str(self.itemCombo.currentText())
        BPType = str(self.typeCombo.currentText())
        runs = int(self.runs.text())
        me = int(self.me.text())
        pe = int(self.pe.text())
        cost = unmoney_me(self.cost.text())

        itemData =  (productID, productName, BPType, runs, me, pe, cost)
        self.KMMdatabase.updateData('''
            INSERT INTO BPassets (productTypeID, ProductTypeName, 
                                  BPtype, runs, me, pe, cost) 
            VALUES (?,?,?,?,?,?,?);
            ''', itemData)
        self.KMMdatabase.commitData()
        self.loadAll()

    def delBP(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected blueprints from the list?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 16384:
            #Yes
            items = []
            for item in self.BPtable.selectedRanges():
                if item.rowCount() == 1:
                    items.append(item.topRow())
                elif item.rowCount() >1:
                    for i in range(item.topRow(), item.bottomRow()+1):
                        items.append(i)
            for row in items:
                ID = int(self.BPtable.verticalHeaderItem(row).text())
                self.KMMdatabase.updateData('''
                    DELETE FROM BPassets 
                    WHERE ID = ?;
                    ''', (ID,))
            self.KMMdatabase.commitData()
        self.loadAll()
    
    def updBP(self):
        if (self.me.text() == "") or (self.pe.text() == "") or (self.runs.text() == "") or self.BPtable.currentRow() == -1:
            return
        row         = self.BPtable.currentRow()
        ID          = int(self.editedID)
        productID   = self.itemCombo.itemData(self.itemCombo.currentIndex()).toInt()[0]
        productName = str(self.itemCombo.currentText())
        BPType      = str(self.typeCombo.currentText())
        runs        = int(self.runs.text())
        me          = int(self.me.text())
        pe          = int(self.pe.text())
        cost        = unmoney_me(self.cost.text())

        itemData =  (productID, productName, BPType, runs, me, pe, cost, ID)

        self.KMMdatabase.updateData('''
            UPDATE BPassets SET productTypeID = ?, ProductTypeName = ?, BPtype = ?, 
                                runs = ?, me = ?, pe = ?, cost = ?
            WHERE ID = ?;
            ''', itemData)
        self.KMMdatabase.commitData()
        self.loadAll()

    def setCombos(self):
        # Sets the BP Item combo
        items = self.EVEdatabase.queryData('''
                SELECT module.typename "Module", module.typeID "typeID"
                FROM invTypes module, invBlueprintTypes bp, invTypes bpitem
                WHERE bp.productTypeID = module.typeID
                AND bp.blueprinttypeID = bpitem.typeID
                AND (module.typeid NOT IN
                      (SELECT typeid FROM invmetatypes WHERE
                       metaGroupID != 1))
                AND NOT (
                        module.typename LIKE '% test %'
                     OR module.typename LIKE 'test%'
                     OR module.typename LIKE '%test'
                     OR module.typename LIKE '%meta%'
                     OR module.typename LIKE '%test'
                     OR module.typename LIKE '% old'
                     OR module.typename LIKE '%unused'
                     OR module.typename LIKE '%tier%'
                     OR module.typename LIKE '"%'
                     OR module.typename LIKE "'%"
                     )
                ORDER BY module.typename;
            ''')
        for module, ID in items:
            self.itemCombo.addItem(module, QtCore.QVariant(ID))
        
        # Sets the BP type combo
        self.typeCombo.addItem("BPO", QtCore.QVariant(1))
        self.typeCombo.addItem("BPC", QtCore.QVariant(2))

    def loadToEdit(self):
        row = self.BPtable.currentRow()
        self.editedID = self.BPtable.verticalHeaderItem(row).text()
        self.itemCombo.setCurrentIndex(self.itemCombo.findText(self.BPtable.item(row,0).text()))
        self.typeCombo.setCurrentIndex(self.typeCombo.findText(self.BPtable.item(row,1).text()))
        self.runs.setText(self.BPtable.item(row,2).text())
        self.me.setText(self.BPtable.item(row,3).text())
        self.pe.setText(self.BPtable.item(row,4).text())
        self.cost.setText(self.BPtable.item(row,5).text())

    def loadMinerals(self):
        stockISK = 0
        for row in range(self.mineralTable.rowCount()):
            self.mineralTable.removeRow(0)
        self.mineralTable.verticalHeader().hide()
        mineralTableCol = ["Mineral", "Quantity", "Isk"]
        self.mineralTable.setColumnCount(len(mineralTableCol))
        self.mineralTable.setHorizontalHeaderLabels(mineralTableCol)

        data = self.KMMdatabase.queryData('''
            SELECT mineral, quantity, cost 
            FROM mineral_stock;
            ''')

        for mineral, quantity, cost in data:
            minISK = quantity*cost
            stockISK += minISK
            row = self.mineralTable.rowCount()
            self.mineralTable.insertRow(row)
            self.mineralTable.setItem(row, 0, QtGui.QTableWidgetItem(mineral))
            self.mineralTable.setItem(row, 1, QtGui.QTableWidgetItem(dot_me(quantity)))
            self.mineralTable.setItem(row, 2, QtGui.QTableWidgetItem(money_me(minISK)))
        self.mineralTable.resizeColumnsToContents()
        self.mineralTable.resizeRowsToContents()
        self.mineralISKTotal = stockISK
        self.mineralISK.setText(money_me(stockISK))
        
    def loadItems(self):
        stockISK = 0
        for row in range(self.itemTable.rowCount()):
            self.itemTable.removeRow(0)

        self.itemTable.verticalHeader().hide()
        itemsTableCol = ["Item", "Quantity", "Build Cost"]
        self.itemTable.setColumnCount(len(itemsTableCol))
        self.itemTable.setHorizontalHeaderLabels(itemsTableCol)

        data = self.KMMdatabase.queryData('''
            SELECT ID, typeID, quantity, PE, BPme, BPpe, locationID, 
                   statusID, quantitysold, capitalship, capitalshipcost
            FROM itemmanufacture 
            WHERE statusID IN (3, 4, 5, 6);''')
        
        for ID, typeID, quantity, pe, BPme, BPpe, locationID, statusID, quantitysold, capitalship, capitalshipcost in data:
            Item = itemObject(ID, typeID, quantity, None, pe, BPme, BPpe, locationID, statusID)
            
            if capitalship == 0:
                itemISK = unmoney_me(Item.getItemCost())
            else:
                itemISK = capitalshipcost
            
            stockISK    += itemISK
            row         = self.itemTable.rowCount()
            self.itemTable.insertRow(row)
            self.itemTable.setItem(row, 0, QtGui.QTableWidgetItem(Item.itemName))
            self.itemTable.setItem(row, 1, QtGui.QTableWidgetItem(str(Item.itemQuantity-quantitysold)))
            self.itemTable.setItem(row, 2, QtGui.QTableWidgetItem(money_me(itemISK)))

        self.itemTable.resizeColumnsToContents()
        self.itemTable.resizeRowsToContents()
        self.itemsISKTotal = stockISK
        self.itemsISK.setText(money_me(stockISK))
        
    def loadBluePrints(self):
        data = self.KMMdatabase.queryData('''
            SELECT ID, productTypeID, productTypeName, 
                   BPType, runs, ME, PE, cost
            FROM BPAssets;''')

        stockISK = 0
        for row in range(self.BPtable.rowCount()):
            self.BPtable.removeRow(0)
        self.BPtable.verticalHeader().hide()
        BPtableCol = ["Product", "Type", "Runs", "ME", "PE", "Cost"]
        self.BPtable.setColumnCount(len(BPtableCol))
        self.BPtable.setHorizontalHeaderLabels(BPtableCol)
        
        for ID, productTypeID, productTypeName, BPType, runs, ME, PE, cost in data:
            row = self.BPtable.rowCount()
            self.BPtable.insertRow(row)
            self.BPtable.setVerticalHeaderItem(row, QtGui.QTableWidgetItem(str(ID)))
            self.BPtable.setItem(row, 0, QtGui.QTableWidgetItem(str(productTypeName)))
            self.BPtable.setItem(row, 1, QtGui.QTableWidgetItem(str(BPType)))
            self.BPtable.setItem(row, 2, QtGui.QTableWidgetItem(str(runs)))
            self.BPtable.setItem(row, 3, QtGui.QTableWidgetItem(str(ME)))
            self.BPtable.setItem(row, 4, QtGui.QTableWidgetItem(str(PE)))
            self.BPtable.setItem(row, 5, QtGui.QTableWidgetItem(str(money_me(cost))))
            stockISK += cost

        self.bpISKTotal = stockISK
        self.BPtable.setColumnWidth(0,200)
        self.BPtable.setColumnWidth(1,50)
        self.BPtable.setColumnWidth(2,40)
        self.BPtable.setColumnWidth(3,30)
        self.BPtable.setColumnWidth(4,30)
        self.BPtable.setColumnWidth(5,90)
        self.BPtable.resizeRowsToContents()


class capitalShipsWindow(internalWindows, Ui_CapitalShips):
    """
    Capital Ships construction window
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.fields = ('self.armor_plates_', 'self.cap_batt_', 'self.cargo_bay_',
                       'self.clone_vat_', 'self.comp_sys_', 'self.const_parts_',
                       'self.corp_hangar_', 'self.dooms_', 'self.drone_', 'self.jump_brid_',
                       'self.jump_drive_', 'self.launcher_', 'self.power_gen_',
                       'self.prop_eng_', 'self.sensor_', 'self.shield_emit_',
                       'self.ship_maint_', 'self.siege_array_', 'self.turret_')
       
        self.componentID = [21017, 21019, 21027, 24547, 21035, 21037, 24560, 24556, 
                            21029, 24545, 21025, 21041, 21021, 21009, 21013, 21023,
                            24558, 21039, 21011]

        self.populateItemCombo()
        self.populateLocationCombo()
        self.populateStatusCombo()
        self.populateFilterCombo()
        self.getSkills()
        self.loadValues()
        self.updateFields()
        self.setupTable()

        self.connect(self.itemCombo, QtCore.SIGNAL("currentIndexChanged(int)"),self.itemSelected)
        self.connect(self.PeSkill, QtCore.SIGNAL("textChanged(QString)"),self.PeChanged)
        self.connect(self.BpMe, QtCore.SIGNAL("textChanged(QString)"),self.MeChanged)
        self.connect(self.BpPe, QtCore.SIGNAL("textChanged(QString)"),self.PeChanged)
        self.connect(self.insertButton, QtCore.SIGNAL("clicked()"),self.insertJob)
        self.connect(self.reloadButton, QtCore.SIGNAL("clicked()"),self.updateFields)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"),self.deleteJob)
        self.connect(self.updateButton, QtCore.SIGNAL("clicked()"),self.updateJob)      
        self.connect(self.viewFilteredButton, QtCore.SIGNAL("clicked()"),self.viewFiltered)
        self.connect(self.locationCombo, QtCore.SIGNAL("activated(int)"),self.locationComboLoad)        
        self.connect(self.prodTable, QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"),self.loadNote)
        self.connect(self.updateNoteButton, QtCore.SIGNAL("clicked()"),self.updateJob)      

    def closeEvent(self, event):
        self.saveValues()
        internalWindows.closeEvent(self, event)

    def saveValues(self):
        bpCost = []
        bpme = []
        market = []
        for i in range(len(self.componentID)):
            bpmeField = str(eval(self.fields[i] + "BPME").text())
            bpcostField = str(eval(self.fields[i] + "BPCOST").text())
            marketField = str(eval(self.fields[i] + "MARKET").text())
            bpme.append(bpmeField)
            bpCost.append(unmoney_me(bpcostField))
            market.append(unmoney_me(marketField))

        self.KMMdatabase.updateData('''INSERT OR REPLACE INTO params
            (name, data) VALUES (?, ?);''', ("bpme",repr(bpme)))
        self.KMMdatabase.updateData('''INSERT OR REPLACE INTO params
            (name, data) VALUES (?, ?);''', ("bpcost",repr(bpCost)))
        self.KMMdatabase.updateData('''INSERT OR REPLACE INTO params
            (name, data) VALUES (?, ?);''', ("market",repr(market)))
        self.KMMdatabase.commitData()

    def loadValues(self):
        data = self.KMMdatabase.queryData('''
            SELECT data 
            FROM params
            WHERE name = "bpme";
            ''')
        if data != []:
            bpme = eval(data[0][0])
        else:
            bpme = [0] * len(self.componentID)
            
        data = self.KMMdatabase.queryData('''
            SELECT data 
            FROM params
            WHERE name = "bpcost";
            ''')
        if data != []:
            bpcost = eval(data[0][0])
        else:
            bpcost = [0] * len(self.componentID)

        data = self.KMMdatabase.queryData('''
            SELECT data 
            FROM params
            WHERE name = "market";
            ''')
        if data != []:
            market = eval(data[0][0])
        else:
            market = [0] * len(self.componentID)

        for componentID, i in zip(self.componentID, range(len(self.componentID))):
            bpmeField = eval(self.fields[i] + "BPME")
            bpcostField = eval(self.fields[i] + "BPCOST")
            marketField = eval(self.fields[i] + "MARKET")

            bpmeField.setText(str(bpme[i]))
            bpcostField.setText(money_me(bpcost[i]))
            marketField.setText(money_me(market[i]))

    def populateItemCombo(self):
        items = self.EVEdatabase.queryData('''
            SELECT module.typename "Ship", module.typeID "typeID"
            FROM invTypes module
            WHERE module.groupID IN (485,513,547,659,30)
            AND module.typeName NOT LIKE ('%test%')
            ORDER BY module.typeName
            ''')
        for module, ID in items:
            self.itemCombo.addItem(module, QtCore.QVariant(ID))

    def populateLocationCombo(self):
        self.locationCombo.clear()
        locations = self.KMMdatabase.queryData('''
            SELECT ID, location 
            FROM locations;
            ''')
        for ID, location in locations:
            self.locationCombo.addItem(location, QtCore.QVariant(ID)) 

    def populateStatusCombo(self):
        statuses = self.KMMdatabase.queryData('''
            SELECT ID, status 
            FROM productionstatus;
            ''')
        for ID, status in statuses:
            self.buildStatusCombo.addItem(status, QtCore.QVariant(ID))

    def populateFilterCombo(self):
        self.filterNames = ['Default', 'Planned','Pre-Production','Building',
                            'Delivered', 'Built','On-Sale','Sold']
        self.filters     = [' statusID >= 1',' statusID like 1',
                            ' statusID like 2',' statusID like 3',
                            ' statusID like 4',' statusID like 5',
                            ' statusID like 6',' statusID like 7']

        for filter in self.filterNames:
            self.filterCombo.addItem(filter) 

    def locationComboLoad(self):
        typedLocation = str(self.locationCombo.currentText())
        loc = []
        locations = self.KMMdatabase.queryData('''
            SELECT location 
            FROM locations;
            ''')
        for location in locations:
            loc.append(location[0])

        if typedLocation not in loc:
            result = QtGui.QMessageBox.question( self, self.tr('Add location'), 
                        self.tr("The location you typed do not exists in database, add it?"),
                        QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
            if result == 16384:
                self.KMMdatabase.updateData('''
                    INSERT INTO locations (location) VALUES (?);
                    ''', (typedLocation,))
                self.KMMdatabase.commitData()
                self.populateLocationCombo()
            else:
                self.populateLocationCombo()

    def getSkills(self):
        skill = self.KMMdatabase.queryData('''
            SELECT skilllevel 
            FROM characterskills 
            WHERE skillID = 3388 
            AND charID = ?;''', (str(self.parent.activeChar[0]),))
        try:
            self.PeSkill.setText(str(skill[0][0]))
        except IndexError:
            QtGui.QMessageBox.critical( self, self.tr('Error'),"No active character found. Go to Skills window and set an active char.",
                            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)

    def insertJob(self):
        typeID      = int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString())
        date        = str(self.date.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        locationID  = int(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        cost        = unmoney_me(self.constructionTotal.text())
        statusID    = int(self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString())

        self.KMMdatabase.updateData('''
            INSERT INTO itemmanufacture 
            (typeID, quantity, date, pe, BPme, BPpe, locationID, capitalshipcost, capitalship, statusID) 
            VALUES (?,?,?,?,?,?,?,?,?,?);
            ''', (typeID, 1, date, pe, BPme, BPpe, locationID, cost,1, statusID))

        self.KMMdatabase.commitData()
        self.setupTable()

    def deleteJob(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected job from the database?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 16384:
            #Yes
            row = self.prodTable.currentRow()
            ID = str(self.prodTable.item(row,0).text())
            self.prodTable.removeRow(row)
            self.KMMdatabase.updateData('''
                DELETE FROM itemmanufacture 
                WHERE ID = ?;
                ''', (ID,))
            self.KMMdatabase.updateData('''
                DELETE FROM constructionnotes
                WHERE constID = ?;
                ''', (ID,))
            self.KMMdatabase.commitData()

    def updateJob(self):
        for row in range(self.prodTable.rowCount()):      
            ID = str(self.prodTable.item(row,0).text())
            statusID = int(self.prodTable.cellWidget(row, 2).itemData(self.prodTable.cellWidget(row, 2).currentIndex()).toString())
            self.KMMdatabase.updateData('''
                UPDATE itemmanufacture SET statusID = ?
                WHERE ID = ?;
                ''', (statusID, ID))
        if self.prodTable.currentRow() != -1:
            ID = str(self.prodTable.item(self.prodTable.currentRow(),0).text())
            note = str(self.constructionNotes.toPlainText())
            self.KMMdatabase.updateData('''
                INSERT OR REPLACE INTO constructionNotes
                (constID, note) VALUES (?, ?);
                ''', (ID, note))
        self.KMMdatabase.commitData()
        self.setupTable()
 
    def loadNote(self):
        row = self.prodTable.currentRow()
        ID = str(self.prodTable.item(row,0).text())
        self.lotIDNote.setText(ID)
        self.shipNameNote.setText(str(self.prodTable.item(row,1).text()))
        try:
            note = self.KMMdatabase.queryData('''
                SELECT note from constructionNotes
                WHERE constID = ?;
                ''', (ID,))
            note = str(note[0][0])
            self.constructionNotes.setPlainText(note)
        except IndexError:
            self.constructionNotes.setPlainText("")

    def viewFiltered(self):
        self.setupTable(self.filterNames[self.filterCombo.currentIndex()])

    def itemSelected(self, index):
        self.getBpMePe(int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString()))
        self.updateFields()

    def PeChanged(self):
        self.updateFields()

    def MeChanged(self):
        self.updateFields()

    def updateFields(self):
        if (self.PeSkill.text() == "") or (self.BpMe.text() == "") or (self.BpPe.text() == ""):
            return
        
        self.date.setText(QtCore.QDate.currentDate().toString("dd/MM/yyyy"))

        typeID      = int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString())
        date        = str(self.date.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        locationID  = str(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        statusID    = self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString()

        for componentID, i in zip(self.componentID, range(len(self.componentID))):
            buildField = eval(self.fields[i] + "BUILD")
            qtField = eval(self.fields[i] + "QT")
            costField = eval(self.fields[i] + "COST")
            bpmeField = eval(self.fields[i] + "BPME")
            bpcostField = eval(self.fields[i] + "BPCOST")
            marketField = eval(self.fields[i] + "MARKET")

            buildField.setText("0")
            qtField.setText("0")
            costField.setText("0")

            BPdata = self.getBpMePe(componentID)
            if BPdata[0] != 999 and BPdata[1] != 999:
                bpmeField.setText(str(BPdata[0]))
                bpcostField.setText(money_me(BPdata[1]))

        bpData = self.EVEdatabase.queryData('''
            SELECT  mat.typeID, mat.typename, comp_mat.quantity,
            bp.wastefactor
            FROM invBlueprintTypes bp, invtypes mat, TL2MaterialsForTypeWithActivity comp_mat,
            invTypes bpitem, invTypes item
            WHERE bp.productTypeID = ?
            AND item.typeID = bp.productTypeID
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            AND mat.groupID = 334
            ORDER BY mat.typename;
            ''', (str(typeID),))

        shipCost = 0.0

        for compID, compName, quantity, waste in bpData:
            buildField = eval(self.fields[self.componentID.index(compID)] + "BUILD")
            qtField = eval(self.fields[self.componentID.index(compID)] + "QT")
            costField = eval(self.fields[self.componentID.index(compID)] + "COST")
            bpmeField = eval(self.fields[self.componentID.index(compID)] + "BPME")
            bpcostField = eval(self.fields[self.componentID.index(compID)] + "BPCOST")
            marketField = eval(self.fields[self.componentID.index(compID)] + "MARKET")

            waste = float(waste)/100
            compBPme = int(bpmeField.text())
            quantity = calculateMinerals(quantity, waste, BPme, pe, 1)
            Item = itemObject(None, compID, 1, date, pe, compBPme, BPpe, locationID, 1)
            BPcost = unmoney_me(bpcostField.text())
            componentMarket = unmoney_me(marketField.text())
            componentBuild = unmoney_me(Item.getItemCost())
            componentBuild = componentBuild + BPcost

            if (componentMarket > componentBuild) or (componentMarket == 0) or (componentMarket == ""):
                bestCost = componentBuild
            else:
                bestCost = componentMarket
            
            componentCost = bestCost*quantity
            shipCost += componentCost

            bpcostField.setText(money_me(unmoney_me(bpcostField.text())))
            marketField.setText(money_me(unmoney_me(marketField.text())))
            buildField.setText(money_me(componentBuild))
            qtField.setText(str(quantity))
            costField.setText(money_me(componentCost))

        self.constructionTotal.setText(money_me(shipCost))

    def getBpMePe(self, itemID):
        data = self.KMMdatabase.queryData('''
            SELECT me, cost 
            FROM BPassets 
            WHERE productTypeID = ?
            ORDER BY me;
            ''', (str(itemID),))
        if data == []:
            return (999,999)
        else:
            return (data[0][0], data[0][1])

    def setupTable(self, filtertype="Default"):
        # Sets the table
        for row in range(self.prodTable.rowCount()):
            self.prodTable.removeRow(0)
        self.prodTable.verticalHeader().hide()

        tableColumns = ["Lot ID.", "Item", "Status","Total Cost", 
                        "Date", "PE", "BP ME", "BP PE",  "Location"]
        self.prodTable.setColumnCount(len(tableColumns))
        self.prodTable.setHorizontalHeaderLabels(tableColumns)

        prodItems = self.KMMdatabase.queryData('''
            SELECT it.ID, it.typeID, st.status, it.capitalshipcost, 
                   it.date, it.PE, it.BPME, it.BPPE, loc.location
            FROM itemmanufacture it, locations loc, productionstatus st
            WHERE capitalship = 1
            AND it.locationID = loc.ID
            AND it.statusID = st.ID 
            AND + ''' + self.filters[self.filterNames.index(filtertype)] + ';')

        if prodItems == []:
            return
        for prodItem in prodItems:

            itemName = self.EVEdatabase.queryData('''
                SELECT typename
                FROM invTypes
                WHERE typeID = ?;
                ''', (str(prodItem[1]),))
            
            itemName = itemName[0][0]
            row = self.prodTable.rowCount()
            self.prodTable.insertRow(row)

            itemData = (prodItem[0],itemName,prodItem[2],money_me(prodItem[3]),
                        prodItem[4],prodItem[5],prodItem[6],prodItem[7],
                        prodItem[8])

            combo = buildStatusCombo(self.prodTable)
            combo.setCurrentIndex(combo.findText(str(prodItem[2])))

            for data, col in zip(itemData, range(self.prodTable.columnCount())):
                if col == 2:
                    self.prodTable.setCellWidget(row, col, combo)
                else:
                    self.prodTable.setItem(row, col, QtGui.QTableWidgetItem(str(data)))

        self.prodTable.resizeColumnsToContents()
        self.prodTable.resizeRowsToContents()
        self.prodTable.setColumnWidth(2, 100)


class salesWindow(internalWindows, Ui_Sales):
    """
    Sales tracking window
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.populateFilterCombo()

        self.setupTable()

        self.connect(self.updateButton, QtCore.SIGNAL("clicked()"),self.updateAll)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.cancelAll)
        self.connect(self.viewFilteredButton, QtCore.SIGNAL("clicked()"),self.viewFiltered)
        self.connect(self.exportButton, QtCore.SIGNAL("clicked()"),self.exportCSVData)

    def updateAll(self):
        for row in range(self.salesTable.rowCount()):
            ID = int(self.salesTable.item(row,0).text())
            sale_date = str(self.salesTable.item(row,2).text())
            sale_loc = self.salesTable.item(row,3).text()
            qt_sold = int(self.salesTable.item(row,5).text())
            status = self.salesTable.item(row,6).text()
            sell_price = float(unmoney_me(self.salesTable.item(row,8).text()))

            try:
                additionalData = self.KMMdatabase.queryData('''
                    SELECT loc.ID FROM locations loc
                    WHERE loc.location = ?;
                    ''', (str(sale_loc),))
                locID = str(additionalData[0][0])
            except IndexError:
                locID = None

            additionalData = self.KMMdatabase.queryData('''
                SELECT stat.ID FROM productionstatus stat
                WHERE stat.status = ?;
                ''', (str(status),))
            statusID = str(additionalData[0][0])

            if not sale_date: sale_date = ""
            if not locID: locID = ""
            if not qt_sold: qt_sold = 0
            if not sell_price: sell_price = 0
            self.KMMdatabase.updateData('''
                UPDATE itemmanufacture 
                SET sale_date = ?, sale_locationID = ? ,quantitysold = ? ,statusID = ?, sell_price = ? 
                WHERE ID = ?;
                ''', (sale_date, locID, qt_sold, statusID, sell_price, ID))
            self.KMMdatabase.commitData()
        self.setupTable()
            
    def cancelAll(self):
         self.setupTable()
         
    def viewFiltered(self):
        self.setupTable(self.filterNames[self.filterCombo.currentIndex()])

    def populateFilterCombo(self):
        self.filterNames = ['All', 'On-Sale','Sold']
        self.filters     = [' statusID in (6,7)',' statusID like 6',
                            ' statusID like 7']
        for filter in self.filterNames:
            self.filterCombo.addItem(filter) 

    def setupTable(self, filtertype="All"):
        # Sets the table
        self.salesTable.setSortingEnabled(False)
        totalMargin = 0
        for row in range(self.salesTable.rowCount()):
            self.salesTable.removeRow(0)
        self.salesTable.verticalHeader().hide()

        tableColumns = ["Lot ID.", "Item", "Sale Date","Sale Location", "Qty Built","Qty Sold", 
                        "Status", "Build Cost/Each", "Sale Price/Each", "Margin",  "Margin %"]

        self.salesTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.salesTable.setColumnCount(len(tableColumns))
        self.salesTable.setHorizontalHeaderLabels(tableColumns)
        self.salesTable.setItemDelegate(SellTableDelegate(self))

        self.salesTable.verticalHeader().hide()

        saleItems = []      #List to hold all items on sold

        Items = self.KMMdatabase.queryData('''
            SELECT ID, typeID, quantity, date, PE, BPME, BPPE, locationID, statusID
            FROM itemmanufacture 
            WHERE ''' + self.filters[self.filterNames.index(filtertype)] + '''
            AND capitalship = 0;
            ''')

        for saleItem in Items:
            Item = itemObject(saleItem[0],saleItem[1],saleItem[2],saleItem[3],
                              saleItem[4],saleItem[5],saleItem[6],saleItem[7],
                              saleItem[8])

            saleData = self.KMMdatabase.queryData('''
                SELECT IFNULL(item.sale_date,''), IFNULL(item.sale_locationID,''),
                       IFNULL(item.quantitysold,'0'), IFNULL(item.sell_price,0)
                FROM itemmanufacture item, locations loc
                WHERE item.ID = ?;
                ''', (str(saleItem[0]),))
            saleData = saleData[0]

            if saleData[1]:
                loc = self.KMMdatabase.queryData('''
                    SELECT location 
                    FROM locations
                    WHERE ID = ?;
                    ''', (str(saleData[1]),))
                loc = loc[0][0]
            else:
                 loc = ""
            itemCost = Item.getItemCost()
            itemquant = Item.itemQuantity
            
            saleItems.append((str(saleItem[0]),
                              str(Item.itemName),
                              str(saleData[0]),
                              QtGui.QTableWidgetItem(str(loc)),
                              str(itemquant),
                              str(saleData[2]),
                              QtGui.QTableWidgetItem(str(Item.status)),
                              money_me(unmoney_me(itemCost)/itemquant),
                              money_me(float(saleData[3])),
                              money_me(unmoney_me(saleData[3])-unmoney_me(itemCost)/itemquant),
                              money_me(((unmoney_me(saleData[3])-unmoney_me(itemCost)/itemquant)/(unmoney_me(itemCost)/itemquant))*100)+"%"
                              ))

        #Capital Ships

        capitalShips = self.KMMdatabase.queryData('''
            SELECT item.ID, item.typeID, IFNULL(item.sale_date,''), IFNULL(item.sale_locationID,''), 
                   quantity, IFNULL(item.quantitysold,'0'), item.statusID, item.capitalshipcost,
                   IFNULL(item.sell_price,0)
            FROM itemmanufacture item
            WHERE ''' + self.filters[self.filterNames.index(filtertype)] + '''
            AND capitalship = 1;''')

        for saleItem in capitalShips:
            if saleItem[3]:
                loc = self.KMMdatabase.queryData('''
                    SELECT location 
                    FROM locations
                    WHERE ID = ?
                    ;''', (str(saleItem[3]),))
                loc = loc[0][0]
            else:
                 loc = ""

            status = self.KMMdatabase.queryData('''
                SELECT status 
                FROM productionstatus
                WHERE ID = ?;
                ''', (str(saleItem[6]),))
            status = status[0][0]

            itemName = self.EVEdatabase.queryData('''
                SELECT item.typename
                FROM invTypes item
                WHERE item.typeID = ?;
                ''', (str(saleItem[1]),))

            saleItems.append((str(saleItem[0]),
                              str(itemName[0][0]),
                              str(saleItem[2]),
                              QtGui.QTableWidgetItem(str(loc)),
                              str(saleItem[4]),
                              str(saleItem[5]),
                              QtGui.QTableWidgetItem(str(status)),
                              money_me(saleItem[7]/saleItem[4]),
                              money_me(float(saleItem[8]/saleItem[4])),
                              money_me(unmoney_me(saleItem[8])-unmoney_me(saleItem[7])),
                              money_me(((unmoney_me(saleItem[8])-unmoney_me(saleItem[7]))/unmoney_me(saleItem[7]))*100)+"%"
                              ))
        for saleItem in saleItems:
            row = self.salesTable.rowCount()
            self.salesTable.insertRow(row)

            totalMargin += unmoney_me(saleItem[9])
            self.salesTable.setItem(row, 0, QtGui.QTableWidgetItem(saleItem[0]))
            self.salesTable.setItem(row, 1, QtGui.QTableWidgetItem(saleItem[1]))
            self.salesTable.setItem(row, 2, QtGui.QTableWidgetItem(saleItem[2]))
            self.salesTable.setItem(row, 3, saleItem[3])
            self.salesTable.setItem(row, 4, QtGui.QTableWidgetItem(saleItem[4]))
            self.salesTable.setItem(row, 5, QtGui.QTableWidgetItem(saleItem[5]))
            self.salesTable.setItem(row, 6, saleItem[6])
            self.salesTable.setItem(row, 7, QtGui.QTableWidgetItem(saleItem[7]))
            self.salesTable.setItem(row, 8, QtGui.QTableWidgetItem(saleItem[8]))
            self.salesTable.setItem(row, 9, QtGui.QTableWidgetItem(saleItem[9]))
            self.salesTable.setItem(row, 10, QtGui.QTableWidgetItem(saleItem[10]))

            self.salesTable.openPersistentEditor(saleItem[3])
            self.salesTable.openPersistentEditor(saleItem[6])

        self.totalMargin.setText(money_me(totalMargin))

        self.salesTable.setSortingEnabled(True)
        self.salesTable.sortItems(0)
        self.salesTable.resizeColumnsToContents()
        self.salesTable.resizeRowsToContents()
        self.salesTable.horizontalHeader().resizeSection(6, 60)

    def exportCSVData(self):
        filePath = QtGui.QFileDialog.getSaveFileName(self, self.tr("Create File"),
            "", self.tr("Any (*.*)"))
        if not filePath: 
            return

        f = open(filePath,'w')
        f.write(";".join(("Lot ID.", "Item", "Quantity", "Status","Total Cost", 
                "Date", "PE", "BP ME", "BP PE",  "Location", "Tritanium",
                "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
                "Megacyte", "Morphite")))
        f.write('\n')
        rows = self.salesTable.rowCount()
        cols =  self.salesTable.columnCount()
        for row in xrange(rows):
            for col in xrange(cols):
                f.write(self.salesTable.item(row, col).text()+';')
            f.write('\n')
        f.close()
        msg = 'Your data has been exported successfully. Your file is in: ' + str(filePath)
        QtGui.QMessageBox.information( self, self.tr('Export Sucessful'), 
            self.tr(msg),
            QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)


# Auxiliary Classes

class SellTableDelegate(QtGui.QItemDelegate):
    def createEditor(self, parent, option, index):
        filterNames = ['On-Sale','Sold']
        filterID = [6,7]
        self.KMMdatabase = KMMdatabase('KMM')

        if index.column() == 3:
            comboBox = QtGui.QComboBox(parent)
            locations = self.KMMdatabase.queryData('''
                SELECT ID, location 
                FROM locations;
                ''')
            for ID, location in locations:
                comboBox.addItem(location, QtCore.QVariant(ID)) 
        elif index.column() == 6:
            comboBox = QtGui.QComboBox(parent)
            for status, ID in zip(filterNames, filterID):
                comboBox.addItem(status, QtCore.QVariant(ID))
        elif index.column() in (2,5,8):
            return QtGui.QLineEdit(parent)
        else:
            return

        self.connect(comboBox, QtCore.SIGNAL("activated(int)"), self.emitCommitData)
        return comboBox

    def setEditorData(self, editor, index):
        if not editor:
            return
        if index.column() in (3,6):
            comboBox = editor
            pos = comboBox.findText(index.model().data(index).toString(),
                                QtCore.Qt.MatchExactly)
            comboBox.setCurrentIndex(pos)
            return
        if index.column() in (2,5,8):
            editor.setText(index.model().data(index).toString())
            return

    def setModelData(self, editor, model, index):
        if not editor:
            return
        if index.column() in (2,5,8):
            model.setData(index, QtCore.QVariant(editor.text()))
            return
        if index.column() in (3,6):
            comboBox = editor
            model.setData(index, QtCore.QVariant(comboBox.currentText()))
            return

    def emitCommitData(self):
        self.emit(QtCore.SIGNAL("commitData(QWidget *)"), self.sender())

