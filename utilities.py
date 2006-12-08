import sys
import re
import locale

def dot_me(amount):
    """
    formats the number to use thousands . separator
    """
    if amount == "": amount = 0
    locale.setlocale(locale.LC_ALL, 'en')
    return locale.format("%.0f", amount, 1)
	
def money_me(amount):
    """
    formats the number to look like money: 1.123,00
    """
    if amount == "": amount = 0
    locale.setlocale(locale.LC_ALL, 'en')
    return locale.format("%.2f", amount, 1)

def unmoney_me(amount):
    """
    inverse of money_me()
    """
    if amount == "": amount = 0
    new = re.sub(",", "", str(amount))
    return float(new)

def undot_me(amount):
    """
    removes the dots in thousands - inverse of dot_me()
    """
    if amount == "": amount = 0
    new = re.sub(",", "", str(amount))
    new = re.sub("\D", "", str(new))
    return float(new)

def int_undot_me(amount):
    """
    removes the dots in thousands - inverse of dot_me()
    """
    if amount == "": amount = 0
    new = re.sub(",", "", str(amount))
    new = re.sub("\D", "", str(new))
    return int(new)

def executable_path():
   """
   return the path of the executable
   """
   if sys.path[0].endswith( '\library.zip' ):
      str = sys.path[0]
      return str[0:len(str) - 12]
   else:
      return sys.path[0]

def calculateMinerals(base, waste, ME, PE, batches):
    """
    Calculates the minerals needed for the production using the characters and BP attributes 
    """
    a = batches*(round(base*(waste/(ME+1))))
    b = batches*((base*(0.25-(0.05*int(PE)))))
    return int(base*batches + a + b)
