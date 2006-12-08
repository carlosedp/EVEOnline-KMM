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
##
## This is the release information for all files related to this project
## Should be updated to match the release and include all build data
##
## $Rev$
## $Date$
##
#############################################################################

# Main application file and application version, condensedname will be used in
# installer exe file. Ex. [CONDENSEDNAME]-Install-[VERSION].exe
MAINAPP = "KMM.py"
VERSION = "1.0"
CONDENSEDNAME = "KMM"

# Company Name
COMPANY = "Kavanagh Productions"

# Project Name
PROJECTNAME = "Kavanagh Manufacture Manager"

# Project Description
PROJECTDESCRIPTION = "KMM"

#Copyright
COPYRIGHT = "2006 Kavanagh Productions"

# Application icon
ICON = "icon.ico"

# Install destination dir and filename. Ex. [DESTINATIONFILE].exe
DESTINATIONFILE = "KMM"

# External files to add to the project
EXTERNALFILES = ["KMM-DB.db","EVE-DB.db","MSVCP71.dll"]

# User files, not overwrite between installs
USERFILES = ["KMM-DB.db"]

# Modules to exclude
EXCLUDES = []

# Modules to include
INCLUDES = ["sip", "pyexpat","encodings.ascii"]

# Compress library files
COMPRESSLIBS = 0

# Directory with library files
LIBSDIR = "lib/"

