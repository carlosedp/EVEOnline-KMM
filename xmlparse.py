import sys, string
from xml.dom import minidom, Node

output = ""

def walk(parent, outFile):                               # [1]
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            attrs = node.attributes                             # [2]
            for attrName in attrs.keys():
                attrNode = attrs.get(attrName)
                attrValue = attrNode.nodeValue
                if attrName == 'typeName':
                    outFile.write(attrValue)
                    skillName = attrValue
                if attrName == 'typeID':
                    outFile.write("|" + attrValue)
                    skillID = attrValue
            content = []                                        # [3]
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
def runxmlparse(inFileName):                                            # [5]
    outFile = open("skills.tmp","w")

    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    walk(rootNode, outFile)

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print 'usage: python test.py infile.xml'
        sys.exit(-1)
    runxmlparse(args[0])


if __name__ == '__main__':
    main()