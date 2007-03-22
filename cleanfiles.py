#############################################################################
##
## Copyright (C) 2006-2006 Mindcast Productions. All rights reserved.
##
## This file is part of the Universal SQL Navigator - UniSQLNav.
## Find more information in: http://code.google.com/p/unisqlnav/
## Contact at carlosedp@gmail.com
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
## $Rev: $
## $Date: 2006-11-09 11:05:27 -0200 (qui, 09 nov 2006) $
##
#############################################################################

import os
import shutil
import glob
import time

class cleanFiles(object):
    def __init__(self, filetype):
            self.pat = filetype
            self.pathWalk()

    def pathWalk(self):
        arglist = []
        os.path.walk("./",self.process,arglist)

    def process(self, arg, dirname, fnames):
        for file in fnames:
            if file.endswith(self.pat):
                if self.pat == ".qrc":
                    outfile = file.split(".")[0] + "_rc.py"
                elif self.pat == ".ui":
                    outfile = file.split(".")[0] + ".py"
                elif self.pat == ".pyc":
                    outfile = file
                elif self.pat == ".pyo":
                    outfile = file

                outfile = os.path.join(dirname, outfile)
                if os.path.isfile(outfile):
                    print "File " + outfile + " deleted."
                    os.remove(outfile)


cleanFiles(".ui")
cleanFiles(".qrc")
cleanFiles(".pyc")
cleanFiles(".pyo")
try:
    shutil.rmtree('dist')
except: pass
try:
    shutil.rmtree('build')
except: pass
try:
    shutil.rmtree('Installer')
except: pass

print "File cleanup done!"
time.sleep(1)