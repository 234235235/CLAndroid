from LIB.Function import Method 
import sys
import clang.cindex as cci
import LIB.Native_Func_Decl_Detector as nfdd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

class LIB:

    def __init__(self,path="",name="",nativeMethods=[]):
        self.path=path
        self.name=name
        self.nativeMethods=nativeMethods

    def __repr__(self):
        return str(self)

    def __str__(self):
        strng =  ("\n ### LIB START ###\n")
        strng += ("### Path: "+self.path+"\n")
        strng += ("### Name: "+self.name+"\n")
        strng += ("### Registered native Methods:\n")

        if (len(self.nativeMethods) == 0):
            strng += "\nNone\n\n"
        
        for nm in self.nativeMethods:
            strng += str(nm)+"\n"

        strng += ("###   LIB END   ###\n")

        return strng

    def setPath(self,path):
        self.path = path

    def setName(self,name):
        self.name = name

    def setMethods(self,methods):
        self.nativeMethods = methods
        
    def getPath(self):
        return self.path

    def getName(self):
        return self.name

    def getNativeMethods(self):
        return self.nativeMethods

    def store(self,outDir):
        #xml structure
        data = ET.Element("LIB")
        name = ET.SubElement(data,"Name")
        path = ET.SubElement(data,"Path")
        nativeMethods = ET.SubElement(data,"NativeMethods")

        path.text = self.path
        name.text = self.name

        for nm in self.nativeMethods:
            nativeMethods = nm.toXML(nativeMethods)

        data = ET.tostring(data)
        pathName = os.path.join(outDir,self.name+".xml")
        i = 0
        while True:
            if (os.path.isfile(pathName)):
                pathName = pathName.split(".xml")[0]+"_"+str(i)+".xml"
            else:
                break
            i += 1

        with open(pathName,"wb") as f:
            f.write(data)

def load(file):
    with open(file,"r") as f:
        doc = minidom.parse(file)
        path = doc.getElementsByTagName("Path")[0].firstChild.nodeValue
        name = doc.getElementsByTagName("Name")[0].firstChild.nodeValue

        nms = doc.getElementsByTagName("NativeMethods")

        nativeMethods = []
        
        for nm in nms[0].getElementsByTagName("Method"):
            nativeMethods.append(Method.fromXML(nm))


        return LIB(path=path,name=name,nativeMethods=nativeMethods)
    

def getRegisteredMethods(file):
    """ no use of clang bad documentation.
    print("FILE: "+file)
    cci.Config.set_library_file(r'S:\Programme\clang\llvm\build\Debug\bin\libclang.dll')
    index = cci.Index.create()
    tu = index.parse(file)
    print("Translation unit:",tu.spelling)
    #find_typerefs(tu.cursor,"JNINativeMethod")
    print(get_info(tu.cursor))
    exit()"""

    return nfdd.getNativeFunctions(file)

def generateLIB(file):
    spl = file.split(os.sep)

    nativeMethods=getRegisteredMethods(file)
    #print("FILE: "+file)
    #print("NVMS:\n"+str(nativeMethods))
    #exit(0)
    return LIB(path=file,
               name=spl[len(spl)-1],
               nativeMethods=nativeMethods)
    
