from PyQt4 import QtCore, QtGui
import time
from ui_minstock import Ui_MineralStock
from ui_production import Ui_Production
from ui_production_hist import Ui_ProductionHist
from ui_skills import Ui_CharacterSkills
from ui_addchar import Ui_addCharacter
from ui_assets import Ui_Assets
from utilities import *
from dbUtils import KMMdatabase
from itemObjects import *

class internalWindows(QtGui.QMainWindow):
    """ 
    Todas as janelas internas instanciam esta classe
    """
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)
        self.name = self.objectName()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        try:
            self.KMMdatabase = KMMdatabase('KMM')
            self.EVEdatabase = KMMdatabase('EVE')
        except Exception, val:
            QtGui.QMessageBox.critical( self, self.tr('Fatal Error'), str(val),
                                        QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
            sys.exit(-1)

    def closeEvent(self, event):
        windowName = self.parent.openwindowsInstances[self]
        self.parent.openwindowsInstances.__delitem__(self)
        self.parent.openwindowsNames.__delitem__(windowName)
        
        try:
            self.KMMdatabase.closeDatabase()
            self.EVEdatabase.closeDatabase()
        except Exception, val:
            QtGui.QMessageBox.critical( self, self.tr('Fatal Error'), str(val),
                                        QtGui.QMessageBox.Ok,QtGui.QMessageBox.NoButton,QtGui.QMessageBox.NoButton)
        event.accept()


#
# Esta classe cria a janela de controle do estoque e preco dos minerais
#

class minStockWindow(internalWindows,Ui_MineralStock):
    """
    Janela de gerenciamento do estoque de minerais
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

        self.populateValues()

    def populateValues(self):
        self.stockISK = 0
        data = self.KMMdatabase.queryData('SELECT fieldID, quantity, IFNULL(cost,0) FROM mineral_stock;')
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
            prodwin = self.parent.openwindowsNames[productionWindow]
            prodwin.updateFields()
        except Exception:
            pass

    def updDatabase(self, ID):
        quant = self.quantFields[ID].text()
        cost = self.costFields[ID].text()
        self.KMMdatabase.updateData('UPDATE OR REPLACE mineral_stock SET quantity = ?, cost = ? WHERE fieldID = ? ;',
                   (undot_me(quant),unmoney_me(cost), ID))


#
# Esta classe cria a janela de gerenciamento de producao
#

class productionWindow(internalWindows,Ui_Production):
    """
    Manages the items manufacturing
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.populateStatusCombo()
        self.populateItemCombo()
        self.populateLocationCombo()
        self.populateFilterCombo()
        self.updateFields()
        self.setupTable()
        self.getSkills()
        self.itemID.hide()

        self.connect(self.itemCombo, QtCore.SIGNAL("currentIndexChanged(int)"),self.itemSelected)
        self.connect(self.quantitySpin, QtCore.SIGNAL("valueChanged(int)"),self.quantityChanged)
        self.connect(self.PeSkill, QtCore.SIGNAL("textChanged(QString)"),self.PeChanged)
        self.connect(self.BpMe, QtCore.SIGNAL("textChanged(QString)"),self.MeChanged)
        self.connect(self.insertButton, QtCore.SIGNAL("clicked()"),self.insertJob)
        self.connect(self.updateButton, QtCore.SIGNAL("clicked()"),self.updateJob)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"),self.deleteJob)
        self.connect(self.viewFilteredButton, QtCore.SIGNAL("clicked()"),self.viewFiltered)
        self.connect(self.prodTable, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),self.loadToEdit)
        self.connect(self.locationCombo, QtCore.SIGNAL("activated(int)"),self.locationComboLoad)        

    def populateStatusCombo(self):
        statuses = self.KMMdatabase.queryData('''
            SELECT ID, status FROM productionstatus;
            ''')
        for ID, status in statuses:
            self.buildStatusCombo.addItem(status, QtCore.QVariant(ID))

#   Implement T2 items one day...
    def populateItemCombo(self):
        items = self.EVEdatabase.queryData('''
            SELECT module.typename "Module", module.typeID "typeID"
            FROM invTypes module, invBlueprintTypes bp, invTypes bpitem
            where bp.productTypeID = module.typeID
            AND ((module.typeid NOT IN (select typeid from invmetatypes)) OR
            module.typeid IN (select typeID from invmetatypes where
            (metaGroupID = 1)))
            AND bp.blueprinttypeID = bpitem.typeID
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
            order by module.typename
            ''')
        for module, ID in items:
            self.itemCombo.addItem(module, QtCore.QVariant(ID))

    def populateLocationCombo(self):
        self.locationCombo.clear()
        locations = self.KMMdatabase.queryData('''
            SELECT ID, location FROM locations;
            ''')
        for ID, location in locations:
            self.locationCombo.addItem(location, QtCore.QVariant(ID)) 

    def populateFilterCombo(self):
        self.filterNames = ['Default', 'Planned','Pre-Production','Building', 'Delivered']
        self.filters     = ['WHERE statusID in (1,2,3,4)','WHERE statusID like 1',
                            'WHERE statusID like 2','WHERE statusID like 3','WHERE statusID like 4']
        for filter in self.filterNames:
            self.filterCombo.addItem(filter) 
                
    def locationComboLoad(self):
        typedLocation = str(self.locationCombo.currentText())
        loc = []
        locations = self.KMMdatabase.queryData('''
            SELECT location FROM locations;
            ''')

        for location in locations:
            loc.append(location[0])
        if typedLocation in loc:
            pass
        else:
            result = QtGui.QMessageBox.question( self, self.tr('Add location'), 
                        self.tr("The location you typed do not exists in database, add it?"),
                        QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
            if result == 3:
                self.KMMdatabase.updateData('''
                    INSERT INTO locations (location) VALUES (?);
                    ''', (typedLocation,))
                self.KMMdatabase.commitData()
            else:
                self.populateLocationCombo()

    def getSkills(self):
        skill = self.KMMdatabase.queryData('''
            SELECT skilllevel 
            FROM characterskills 
            WHERE skillID = 3388 
            AND charID = 1;
            ''')
        self.PeSkill.setText(str(skill[0][0]))
        #TODO - Set active character

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
       
        self.KMMdatabase.updateData('''
            INSERT INTO itemmanufacture 
            (typeID, quantity, date, pe, BPme, BPpe, locationID, statusID) 
            VALUES (?,?,?,?,?,?,?,?);
            ''', Item.getKMMDatabaseData())

        self.KMMdatabase.commitData()
        self.setupTable()


    def updateJob(self):
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

        self.KMMdatabase.updateData('''
            UPDATE itemmanufacture SET typeID = ?, quantity = ?, date = ?, 
            pe = ?, BPme = ?, BPpe = ?, locationID = ?, statusID = ?
            WHERE ID = ?;
            ''', itemData)
        self.KMMdatabase.commitData()
        self.setupTable()
        try:
            self.parent.openwindowsNames[productionHistWindow].setupTable()
            self.parent.openwindowsNames[assetsWindow].loadAll()
        except Exception:
            pass

    def deleteJob(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected job from the database?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 3:
            #Yes
            row = self.prodTable.currentRow()
            ID = str(self.prodTable.item(row,0).text())
            self.prodTable.removeRow(row)
            self.KMMdatabase.updateData('''
                DELETE FROM itemmanufacture WHERE ID = ?;
                ''', (ID,))
            self.KMMdatabase.commitData()
     
    def viewFiltered(self):
        self.setupTable(self.filterNames[self.filterCombo.currentIndex()])
  
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
        self.updateFields()

    def setupTable(self, type="Default"):
        # Sets the table
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
            FROM itemmanufacture ''' + self.filters[self.filterNames.index(type)] + ';')
            
        if prodItems == []:
            return
        for prodItem in prodItems:
            row = self.prodTable.rowCount()
            self.prodTable.insertRow(row)
            Item = itemObject(prodItem[0],prodItem[1],prodItem[2],prodItem[3],
                              prodItem[4],prodItem[5],prodItem[6],prodItem[7],
                              prodItem[8])

            itemData = Item.getTableData()

            for data, col in zip(itemData, range(self.prodTable.columnCount())):
                self.prodTable.setItem(row, col, QtGui.QTableWidgetItem(str(data)))

        self.prodTable.resizeColumnsToContents()
        self.prodTable.resizeRowsToContents()

    def itemSelected(self):
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
        self.date.setText(time.strftime("%d/%m/%Y", time.localtime(time.time())))

        typeID      = int(self.itemCombo.itemData(self.itemCombo.currentIndex()).toString())
        quantity    = int(self.quantitySpin.value())
        date        = str(self.date.text())
        pe          = int(self.PeSkill.text())
        BPme        = int(self.BpMe.text())
        BPpe        = int(self.BpPe.text())
        locationID  = str(self.locationCombo.itemData(self.locationCombo.currentIndex()).toString())
        statusID    = self.buildStatusCombo.itemData(self.buildStatusCombo.currentIndex()).toString()

        self.getBpMePe(typeID)
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
            WHERE bp.productTypeID = ''' + str(typeID) + '''
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            order by mat.typeID''')

        materials = Item.getTableData()
        costEach  = 0

        minCost     = {}
        minStock    = {}
        
        minCosts = self.KMMdatabase.queryData('''
            SELECT ID, cost, quantity 
            FROM mineral_stock 
            ORDER BY ID;''')

        for min_ID, min_cost, min_stock in minCosts:
            minCost[min_ID]  = min_cost
            minStock[min_ID] = min_stock

        for matQuantity, i in zip(materials[-8:], range(len(matFormFieldsTotal))):
            matFormFieldsTotal[i].setText(dot_me(matQuantity*quantity))
            matFormFieldsEach[i].setText(dot_me(matQuantity))
            costEach += matQuantity*minCost[matTypeID[i]]
            
            if (matQuantity*quantity) > minStock[matTypeID[i]]:
               matFormFieldsTotal[i].setText("<font color='red'>" + matFormFieldsTotal[i].text() + "</font>")
            
        self.costEach.setText(money_me(costEach))
        self.costTotal.setText(money_me(costEach*quantity))

    def getBpMePe(self, itemID):
        data = self.KMMdatabase.queryData('''
            SELECT me, pe FROM BPassets WHERE productTypeID = ''' + str(itemID) +';')
        if data == []:
            me = 0
            pe = 0
        else:
            me = data[0][0]
            pe = data[0][1]
        self.BpMe.setText(str(me))
        self.BpPe.setText(str(pe))

#
# Esta classe cria a janela para a inclusao de um novo personagem
#

class addCharWindow(internalWindows, Ui_addCharacter):
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

#
# Esta classe cria a janela de gerenciamento das skills do personagem
#

class skillsWindow(internalWindows,Ui_CharacterSkills):

    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.connect(self.addCharButton, QtCore.SIGNAL("clicked()"),self.addCharWindow)
        self.connect(self.saveButton, QtCore.SIGNAL("clicked()"),self.saveSkills)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.loadSkills)
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
        self.loadSkills()

    def populateChars(self):
        data = self.KMMdatabase.queryData('''
            SELECT ID, name
            FROM characters;
            ''')
        if data != []:
            for ID, name in data:
                self.characterCombo.addItem(name, QtCore.QVariant(ID)) 

    def loadSkills(self):
        self.charID = str(self.characterCombo.itemData(self.characterCombo.currentIndex()).toString())
        levels = self.KMMdatabase.queryData('''
            SELECT skillID, skillLevel 
            FROM characterskills
            WHERE charID = ''' + self.charID + ';')
        for ID, level in levels:
            self.skillFields[self.skillID.index(ID)].setText(str(level))
            
    def addCharWindow(self):
        self.parent.openWindow(addCharWindow)

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

#
# Esta classe cria a janela de historico de producao
#

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
        self.connect(self.prodTable, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),self.loadToEdit)

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
        self.KMMdatabase.commitData()
        self.setupTable()
        try:
            self.parent.openwindowsNames[productionWindow].setupTable()
            self.parent.openwindowsNames[assetsWindow].loadAll()
        except Exception:
            pass
     
    def deleteJob(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected job from the database?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 3:
            #Yes
            row = self.prodTable.currentRow()
            ID = str(self.prodTable.item(row,0).text())
            self.prodTable.removeRow(row)
            self.KMMdatabase.updateData('''
            DELETE FROM itemmanufacture WHERE ID = ?;
            ''', (ID,))
            self.KMMdatabase.commitData()
 
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
     
    def setupTable(self, type="Default"):
        # Sets the table
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
            FROM itemmanufacture ''' + self.filters[self.filterNames.index(type)] + ';')
            
        if prodItems == []:
            return
        for prodItem in prodItems:
            row = self.prodTable.rowCount()
            self.prodTable.insertRow(row)

            Item = itemObject(prodItem[0],prodItem[1],prodItem[2],prodItem[3],
                              prodItem[4],prodItem[5],prodItem[6],prodItem[7],
                              prodItem[8])

            itemData = Item.getTableData()

            for data, col in zip(itemData, range(self.prodTable.columnCount())):
                self.prodTable.setItem(row, col, QtGui.QTableWidgetItem(str(data)))

        self.prodTable.resizeColumnsToContents()
        self.prodTable.resizeRowsToContents()

    def populateFilterCombo(self):
        self.filterNames = ['Default', 'Built','On-Sale','Sold']
        self.filters     = ['WHERE statusID in (5,6,7)','WHERE statusID like 5',
                            'WHERE statusID like 6','WHERE statusID like 7']
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
            WHERE typeName LIKE "''' + str(self.editItem.text()) + '";')
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
            WHERE bp.productTypeID = ''' + str(typeID) + '''
            AND bp.blueprinttypeID = bpitem.typeID
            AND bpitem.typeID = comp_mat.typeID
            AND mat.typeID = comp_mat.requiredTypeID
            AND comp_mat.activity = 1
            ORDER BY mat.typeID''')

        materials = Item.getTableData()
        costEach  = 0

        minCost  = {}
        minStock = {}
        minCosts = self.KMMdatabase.queryData('''
            SELECT ID, cost, quantity 
            FROM mineral_stock 
            ORDER BY ID;''')

        for min_ID, min_cost, min_stock in minCosts:
            minCost[min_ID] = min_cost
            minStock[min_ID] = min_stock

        for matQuantity, i in zip(materials[-8:], range(len(matFormFieldsTotal))):
            matFormFieldsTotal[i].setText(dot_me(matQuantity*quantity))
            matFormFieldsEach[i].setText(dot_me(matQuantity))
            costEach += matQuantity*minCost[matTypeID[i]]
            if (matQuantity*quantity) > minStock[matTypeID[i]]:
               matFormFieldsTotal[i].setText("<font color='red'>" + matFormFieldsTotal[i].text() + "</font>")
            
        self.costEach.setText(money_me(costEach))
        self.costTotal.setText(money_me(costEach*quantity))

#
# Esta classe cria a janela de gerenciamento dos bens
#

class assetsWindow(internalWindows,Ui_Assets):
    """
    Janela de gerenciamento dos assets
    """
    def __init__(self, parent):
        internalWindows.__init__(self, parent)

        self.loadMinerals()
        self.loadItems()
        self.setCombos()
        self.loadBluePrints()
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"),self.addBP)
        self.connect(self.delButton, QtCore.SIGNAL("clicked()"),self.delBP)
        self.connect(self.updButton, QtCore.SIGNAL("clicked()"),self.updBP)
        self.connect(self.BPtable, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),self.loadToEdit)

    def loadAll(self):
        self.loadMinerals()
        self.loadItems()
        self.loadBluePrints()

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
        self.loadBluePrints()

    def delBP(self):
        result = QtGui.QMessageBox.question( self, self.tr('Remove Job'), 
                    self.tr("Do you want to remove the selected blueprint from the list?"),
                    QtGui.QMessageBox.Yes,QtGui.QMessageBox.No,QtGui.QMessageBox.NoButton)
        if result == 3:
            #Yes
            row = self.BPtable.currentRow()
            ID = int(self.BPtable.verticalHeaderItem(row).text())
            self.BPtable.removeRow(row)
            self.KMMdatabase.updateData('''
                DELETE FROM BPassets 
                WHERE ID = ?;
                ''', (ID,))
            self.KMMdatabase.commitData()
    
    def updBP(self):
        row         = self.BPtable.currentRow()
        ID          = int(self.BPtable.verticalHeaderItem(row).text())
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
        self.loadBluePrints()

    def setCombos(self):
        # Sets the BP Item combo
        items = self.EVEdatabase.queryData('''
            SELECT module.typename "Module", module.typeID "typeID"
            FROM invTypes module, invBlueprintTypes bp, invTypes bpitem
            WHERE bp.productTypeID = module.typeID
            AND ((module.typeid NOT IN (select typeid from invmetatypes)) OR
            module.typeid IN (select typeID from invmetatypes where
            (metaGroupID = 1)))
            AND bp.blueprinttypeID = bpitem.typeID
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
            ORDER BY module.typename
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
            FROM mineral_stock;''')
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
                   statusID, quantitysold
            FROM itemmanufacture 
            WHERE statusID IN (3, 4, 5, 6);''')

        for ID, typeID, quantity, pe, BPme, BPpe, locationID, statusID, quantitysold in data:

            Item = itemObject(ID, typeID, quantity, None, pe, BPme, BPpe, locationID, statusID)

            itemData    = Item.getTableData()
            itemISK     = unmoney_me(itemData[4])
            stockISK    += itemISK
            row         = self.itemTable.rowCount()
            self.itemTable.insertRow(row)
            self.itemTable.setItem(row, 0, QtGui.QTableWidgetItem(itemData[1]))
            self.itemTable.setItem(row, 1, QtGui.QTableWidgetItem(str(itemData[2]-quantitysold)))
            self.itemTable.setItem(row, 2, QtGui.QTableWidgetItem(itemData[4]))

        self.itemTable.resizeColumnsToContents()
        self.itemTable.resizeRowsToContents()

        self.itemsISK.setText(money_me(stockISK))
        
        total = unmoney_me(self.mineralISK.text()) + unmoney_me(self.itemsISK.text())
        self.total.setText(money_me(total))

    def loadBluePrints(self):
        data = self.KMMdatabase.queryData('''
            SELECT ID, productTypeID, productTypeName, 
                   BPType, runs, ME, PE, cost
            FROM BPAssets;''')

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

        self.BPtable.setColumnWidth(0,200)
        self.BPtable.setColumnWidth(1,50)
        self.BPtable.setColumnWidth(2,40)
        self.BPtable.setColumnWidth(3,30)
        self.BPtable.setColumnWidth(4,30)
        self.BPtable.setColumnWidth(5,90)
        self.BPtable.resizeRowsToContents()


