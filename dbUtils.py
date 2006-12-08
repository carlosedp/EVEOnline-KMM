import os
import sys

from pysqlite2 import dbapi2 as sqlite
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


    def queryData(self, query):
      """
      Load data from the SQL database
      """
      self.cursor.execute( query )
      return self.cursor.fetchall()

    def updateData(self, query, data):
        """
        Updates or inserts data into the database
        """
        self.cursor.execute(query, data)

    def commitData(self):
        self.connection.commit()


    def closeDatabase(self):
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

