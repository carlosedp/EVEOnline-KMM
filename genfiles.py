#############################################################################
##
## Copyright (C) 2006-2006 Kavanagh Productions. All rights reserved.
##
## This file is part of the Kavanagh Productions Projects
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

import os
import glob
import time

class processFiles(object):
    def __init__(self, pat, command):
            self.pat = pat
            self.command = command
            self.pathWalk()

    def pathWalk(self):
        arglist = []
        os.path.walk("./",self.process,arglist)

    def process(self, arg, dirname, fnames):
        for file in fnames:
            if file.endswith(str(self.pat)):
                outfile = file.split(".")[0] + ".py"
                outfile = os.path.join(dirname, outfile)
                outcommand = self.command + " " + os.path.join(dirname, file) + " -o " + outfile
                print "File " + outfile + " created."
                os.system(outcommand)    

uifiles = processFiles(".ui", "pyuic4")
resfiles = processFiles(".qrc", "pyrcc4")
print ""

#Translation only
#os.system("pylupdate4 -verbose ./KMM.pro")
#os.system("lrelease -verbose ./KMM.pro")

print ""
print "QT files generation done"
time.sleep(1)