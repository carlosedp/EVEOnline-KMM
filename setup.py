#############################################################################
##
## Copyright (C) 2006-2006 Kavanagh Productions. All rights reserved.
##
## This file is part of the Kavanagh Manufacture Manager - KMM.
## Find more information in: http://
## Contact at cedepaula@yahoo.com.br
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

from distutils.core import setup
import sys
try: import py2exe
except ImportError: pass

########### Do not touch, configure the parameters in the section below ######

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

################### Installer - Inno Setup ####################################
import os

class InnoScript:
    def __init__(self,
                 name,
                 lib_dir,
                 dist_dir,
                 windows_exe_files = [],
                 lib_files = [],
                 version = "1.0"):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]
    
    def create(self, pathname="dist\\setup_file.iss"):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
#        print >> ofi, r"Compression=bzip"
        print >> ofi, r"Compression=lzma/max"
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi
        print >> ofi, r"[Tasks]"
        print >> ofi, r'Name: "quicklaunchicon"; Description: "Create Quicklink Icon"; GroupDescription: "Program Options:"; Flags: checkedonce '
        print >> ofi, r'Name: "desktopicon"; Description: "Create Desktop Icon"; GroupDescription: "Program Options:"; Flags: checkedonce '

        print >> ofi
        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"' % \
                  (self.name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name
        print >> ofi, 'Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\%s"; Filename: "{app}\%s"; Tasks: quicklaunchicon' % (self.name, path)
        print >> ofi, 'Name: "{userdesktop}\%s"; Filename: "{app}\%s"; Tasks: desktopicon' % (self.name, path)

    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api."
                win32api.ShellExecute(0, "compile",
                                                self.pathname,
                                                None,
                                                None,
                                                0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


################################################################

from py2exe.build_exe import py2exe

class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)

        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        
        # create the Installer, using the files py2exe has created.
        script = InnoScript(app.name,
                            lib_dir,
                            dist_dir,
                            self.windows_exe_files,
                            self.lib_files,
                            app.version)
        print "*** creating the inno setup script***"
        script.create()
        print "*** compiling the inno setup script***"
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

######### Configure application here ###########################

app = Target(
    company_name = "Kavanagh Productions",          # Company
    name = "Kavanagh Manufacture Manager",          # Product Name
    description = "KMM",                            # Description
    version = "0.0.3",                              # Version
    copyright = "2006 Kavanagh Productions",        # Copyright
    script = "KMM.py",                              # Script name
    icon_resources = [(1, "icon.ico")],             # Script Icon
    dest_base = "KMM",                              # Destination directory/filename
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="KMM"))])


external_files = [("",["KMM-DB.db","EVE-DB.db"])]   # [("dest. directory",["file1.txt","file2.txt"])]
excludes = []                                       # Modules to exclude
includes = ["sip"]                                  # Modules to include
zipfile = "library.zip"                             # Library filename

######### End of application configuration #####################

setup(
    options = {"py2exe": {"compressed": 1,
                          "optimize": 2,
                          "bundle_files": 3,        # 1-Library.zip | 2- Library.zip + python24.dll | 3- Only modules in Library.zip
                          "includes": includes,
                          "excludes": excludes}},
    zipfile = zipfile,
    windows = [app],
    # use out build_installer class as extended py2exe build command
    cmdclass = {"py2exe": build_installer},
    data_files = external_files
    )
