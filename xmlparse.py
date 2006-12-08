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

import sys, string
from xml.dom import minidom, Node

output = ""

def walk(parent, outFile):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            attrs = node.attributes 
            for attrName in attrs.keys():
                attrNode = attrs.get(attrName)
                attrValue = attrNode.nodeValue
                if attrName == 'typeName':
                    outFile.write(attrValue)
                    skillName = attrValue
                if attrName == 'typeID':
                    outFile.write("|" + attrValue)
                    skillID = attrValue
            content = []
            for child in node.childNodes:
                if child.nodeType == Node.TEXT_NODE:
                    content.append(child.nodeValue)
            if content:
                strContent = string.join(content)
                if node.nodeName == 'level':
                    outFile.write("|" + strContent)
                    skillLevel = strContent
                
            walk(node, outFile)
        if node.nodeName == 'skill':
                outFile.write("\n")
#                print skillName, skillID, skillLevel

def runxmlparse(inFileName):
    outFile = open("skills.tmp","w")

    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    walk(rootNode, outFile)

# Used to test the application
def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print 'usage: python xmlparse.py CharSkills.xml'
        sys.exit(-1)
    runxmlparse(args[0])


if __name__ == '__main__':
    main()