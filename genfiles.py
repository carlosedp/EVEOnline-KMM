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