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
#import psyco

from PyQt4 import QtCore, QtGui

#import resources
import releaseinfo
from internalwin import *
from UI.ui_mainwindow import Ui_MainWindow

#psyco.log()
#psyco.full()

#--- Application Start

class mainWindow(QtGui.QMainWindow, Ui_MainWindow):

    openwindowsNames = {}
    openwindowsInstances = {}
    activeChar = [0,""]

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
        self.workspace = QtGui.QWorkspace()
        self.setCentralWidget(self.workspace)

        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.readSettings()
        self.configureActions()

        self.statusline = QtGui.QFrame(self.statusbar)
        self.statusline.setFrameShape(QtGui.QFrame.VLine)
        self.statusline.setObjectName("statusline")

        self.status1 = QtGui.QLabel(self.statusbar)
        self.statusbar.addPermanentWidget(self.statusline)
        self.statusbar.addPermanentWidget(self.status1)
        self.status1.setText("Active Char: " + self.activeChar[1] + "  ")
        self.statusbar.showMessage("Character loaded...",5000)

    def readSettings(self):
        settings = QtCore.QSettings("Kavanagh Productions", "KMM")
        pos = settings.value("mainpos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("mainsize", QtCore.QVariant(self.size())).toSize()
        self.activeChar = eval(str(settings.value("activeChar",QtCore.QVariant(repr(self.activeChar))).toString()))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings("Kavanagh Productions", "KMM")
        settings.setValue("mainpos", QtCore.QVariant(self.pos()))
        settings.setValue("mainsize", QtCore.QVariant(self.size()))
        settings.setValue("activeChar", QtCore.QVariant(repr(self.activeChar)))

    def configureActions(self):
        # Toolbar actions
        self.connect(self.actionMineral_Stock, QtCore.SIGNAL("triggered()"),self.actionMineral_Stock_Clicked)
        self.connect(self.actionProduction, QtCore.SIGNAL("triggered()"),self.actionProduction_Clicked)
        self.connect(self.actionProduction_History, QtCore.SIGNAL("triggered()"),self.actionProduction_History_Clicked)
        self.connect(self.actionCapital_Ship_Construction, QtCore.SIGNAL("triggered()"),self.actionCapital_Ship_Construction_Clicked)
        self.connect(self.actionAssets, QtCore.SIGNAL("triggered()"),self.actionAssets_Clicked)
        self.connect(self.actionSales, QtCore.SIGNAL("triggered()"),self.actionSales_Clicked)
        self.connect(self.actionGeneral_Costs, QtCore.SIGNAL("triggered()"),self.actionGeneral_Costs_Clicked)
        self.connect(self.actionSkills, QtCore.SIGNAL("triggered()"),self.actionSkills_Clicked)

        # Menus
        self.connect(self.actionE_xit, QtCore.SIGNAL("triggered()"), self.programExit)
        self.connect(self.action_Help, QtCore.SIGNAL("triggered()"), self.programHelp)
        self.connect(self.actionAbout, QtCore.SIGNAL("triggered()"), self.programAbout)
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"), self.updateWindowMenu)

        # Menu Actions
        self.closeAct = QtGui.QAction(self.tr("Cl&ose"), self)
        self.closeAct.setShortcut(self.tr("Ctrl+F4"))
        self.closeAct.setStatusTip(self.tr("Close the active window"))
        self.connect(self.closeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveWindow)

        self.closeAllAct = QtGui.QAction(self.tr("Close &All"), self)
        self.closeAllAct.setStatusTip(self.tr("Close all the windows"))
        self.connect(self.closeAllAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction(self.tr("&Tile"), self)
        self.tileAct.setStatusTip(self.tr("Tile the windows"))
        self.connect(self.tileAct, QtCore.SIGNAL("triggered()"), self.workspace.tile)

        self.cascadeAct = QtGui.QAction(self.tr("&Cascade"), self)
        self.cascadeAct.setStatusTip(self.tr("Cascade the windows"))
        self.connect(self.cascadeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascade)

        self.arrangeAct = QtGui.QAction(self.tr("Arrange &icons"), self)
        self.arrangeAct.setStatusTip(self.tr("Arrange the icons"))
        self.connect(self.arrangeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction(self.tr("Ne&xt"), self)
        self.nextAct.setShortcut(self.tr("Ctrl+F6"))
        self.nextAct.setStatusTip(self.tr("Move the focus to the next window"))
        self.connect(self.nextAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction(self.tr("Pre&vious"), self)
        self.previousAct.setShortcut(self.tr("Ctrl+Shift+F6"))
        self.previousAct.setStatusTip(self.tr("Move the focus to the previous "
                                              "window"))
        self.connect(self.previousAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)


    # Toolbar items functions
    def actionMineral_Stock_Clicked(self):
        self.openWindow(minStockWindow)

    def actionProduction_Clicked(self):
        self.openWindow(productionWindow)

    def actionProduction_History_Clicked(self):
        self.openWindow(productionHistWindow)

    def actionCapital_Ship_Construction_Clicked(self):
        self.openWindow(capitalShipsWindow)

    def actionAssets_Clicked(self):
        self.openWindow(assetsWindow)

    def actionSales_Clicked(self):
        self.openWindow(salesWindow)

    def actionGeneral_Costs_Clicked(self):
        pass

    def actionSkills_Clicked(self):
        self.openWindow(skillsWindow)

    # Menu items functions
    def programHelp(self):
        # TODO: Create program help
        QtGui.QMessageBox.about(self, self.tr("Kavanagh Manufacture Management Help"),
            self.tr("Displays the program help"))

    def programAbout(self):
        # TODO: Create program about
        QtGui.QMessageBox.about(self, self.tr("About KMM"),
            self.tr("Kavanagh Manufacture Manager\nVersion ")+ releaseinfo.VERSION + "\nBuild $Rev$")

    # Event functions
    def closeEvent(self, event):
        event.accept()
        self.programExit()

    # Application functions
    def programExit(self):
        self.writeSettings()
        self.workspace.closeAllWindows()
        sys.exit()

    def openWindow(self, window):
        if self.openwindowsNames.__contains__(window):
            self.workspace.setActiveWindow(self.openwindowsNames[window])
        else:
            internal_window = window(self)
            self.workspace.addWindow(internal_window)   # Adiciona a janela ao workspace
            internal_window.show()
            self.openwindowsNames.update({window: internal_window})
            self.openwindowsInstances.update({internal_window: window})
            #return internal_window

    # Builds the "window" menu with all open windows
    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.workspace.windowList()
        self.separatorAct.setVisible(len(windows) != 0)        
        i = 0
        for child in windows:
            if i < 9:
                text = self.tr("&%1 %2").arg(i + 1).arg(child.windowTitle())
            else:
                text = self.tr("%1 %2").arg(i + 1).arg(child.windowTitle())
            i += 1
            
            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.windowMapper, QtCore.SLOT("map()"))
            self.windowMapper.setMapping(action, child)

    def activeMdiChild(self):
        return self.workspace.activeWindow()

#--- Runs the main app
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    defaultFont = QtGui.QFont()
    defaultFont.setFamily("Lucida Sans Unicode")
    defaultFont.setPointSize(8)
    #defaultFont.setWeight(50)
    defaultFont.setItalic(False)
    defaultFont.setUnderline(False)
    defaultFont.setStrikeOut(False)
    defaultFont.setBold(False)
    app.setFont(defaultFont)

    mainwindow = mainWindow()

    mainwindow.show()
    sys.exit(app.exec_())
