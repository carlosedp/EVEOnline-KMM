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
#############################################################################

import os
import sys

import sqlite3 as sqlite
from utilities import *


class KMMdatabase(object):
    """
    This class provides the methods to access the database
    """

    def __init__(self, db):
      """
      Create the KMMdatabase object
      """
      if db == 'KMM':
          self.database = os.path.join( executable_path(), 'KMM-DB.db' )
      elif db == 'EVE':
          self.database = os.path.join( executable_path(), 'EVE-DB.db' )

      if not os.access( self.database, os.F_OK ):
         msg = ( 'The database file "' + self.database + 
                 '" does not exist' )
         raise DatabaseException( msg )
      if not os.access( self.database, os.R_OK ):
         msg = ( 'The database file "' + self.database + 
                 '" does not have read permissions' )
         raise DatabaseException( msg )
      if not os.access( self.database, os.W_OK ):
         msg = ( 'The database file "' + self.database + 
                 '" does not have write permissions' )
         raise DatabaseException( msg )

      self.connection = sqlite.connect( self.database, 10.0 )
      self.connection.text_factory = sqlite.OptimizedUnicode
      self.cursor = self.connection.cursor()


    def queryData(self, query, data=""):
      """
      Load data from the SQL database
      """
      self.cursor.execute(query, data)
      return self.cursor.fetchall()

    def updateData(self, query, data):
        """
        Updates or inserts data into the database
        """
        self.cursor.execute(query, data)

    def commitData(self):
        """
        Commits the data
        """
        self.connection.commit()

    def rollbackData(self):
        """
        Roll back current transaction
        """
    	self.connection.rollback()

    def closeDatabase(self):
        """
        Closes the database instance
        """
        self.connection.close()


class DatabaseException(Exception): 
    """
    Exception for problems accessing the stock database
    """
    def __init__( self, reason ):
      Exception.__init__( self )
      self.reason = reason

    def __str__( self ):
      return 'Unable to access database: ' + self.reason
