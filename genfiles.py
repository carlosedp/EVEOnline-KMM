import os, glob

class processFiles(object):
    def __init__(self, pat, command):
            self.pat = pat
            self.command = command
            self.gencom()

    def gencom(self):
        files = glob.glob(self.pat)
        for file in files:
            outfile = file.split(".")[0] + ".py"
            outcommand = self.command + " " + file + " -o " + outfile
            print "File " + outfile + " created."
            os.system(outcommand)    


uifiles = processFiles("*.ui", "pyuic4")
resfiles = processFiles("*.qrc", "pyrcc4")
