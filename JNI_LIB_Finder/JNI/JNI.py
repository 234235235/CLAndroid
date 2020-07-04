# -*- coding: cp1252 -*-
import re
from JNI.Function import Method,Parameter
import java_parser.plyj.parser as jp
import xml.etree.ElementTree as ET
from xml.dom import minidom
from Helper.helper import cprint
import sys
import pathlib
import os

path = pathlib.Path(__file__).parent.absolute().parent.parent
sys.path.append(str(path))

from Default.Colors import Color


tag =Color.ORANGE.value+"[JNI] "+Color.RESET.value

class JNI:
    
    def __init__(self,path="",name="",nativeMethods=[],callingNativeMethods=[]):
        self.path = path
        self.name = name
        self.nativeMethods = nativeMethods
        self.callingNativeMethods = callingNativeMethods

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        strng =  ("\n###  JNI START  ###\n")
        strng += ("### Path: "+self.path+"\n")
        strng += ("### Name: "+self.name+"\n")
        
        strng += ("### Declared Native Methods: \n")
        if (len(self.nativeMethods) == 0):
            strng += "\nNone\n\n"
            
        for method in self.nativeMethods:            
            strng += str(method)+"\n"
            
        strng += ("### Methods calling native methods: \n")

        if (len(self.callingNativeMethods) == 0):
            strng += "\nNone\n\n"
            
        for nnat in self.callingNativeMethods:
            strng += str(nnat)+"\n"

        strng += ("###   JNI END   ###\n")

        return strng
    
    def setPath(self,path):

        self.path = path

    def setName(self,name):
        self.name = name

    def setMethods(self,methods):
        self.nativeMethods = methods

    def addNativeMethod(self,method):
        self.nativeMethods.append(method)

    def nativeMethods(self,methods):
        self.nativeMethods.extends(methods)

    def getPath(self):
        return self.path

    def getName(self):
        return self.name

    def getNativeMethods(self):
        return self.nativeMethods
    
    def store(self,outDir):
        #xml structure
        data = ET.Element('JNI')
        name = ET.SubElement(data,"Name")
        path = ET.SubElement(data,'Path')
        nativeMethods = ET.SubElement(data,"NativeMethods")
        callingNativeMethods = ET.SubElement(data,"CallingNativeMethods")
        #path.set("value",self.path)
        path.text = self.path
        name.text = self.name

        for nm in self.nativeMethods:
            nativeMethods = nm.toXML(nativeMethods)
                
        for cnm in self.callingNativeMethods:
            callingNativeMethods = cnm.toXML(callingNativeMethods)

        data = ET.tostring(data)
        pathName = os.path.join(outDir,self.name+".xml")
        i=0

        while True:
            if (os.path.isfile(pathName)):
                pathName = pathName.split(".xml")[0]+"_"+str(i)+".xml"
            else:
                break
            i += i
        
        with open(pathName,"wb") as f:
            f.write(data)

def load(file):
    with open(file,"r") as f:
        doc = minidom.parse(file)
        path = doc.getElementsByTagName("Path")[0].firstChild.nodeValue
        name = doc.getElementsByTagName("Name")[0].firstChild.nodeValue

        nms =  doc.getElementsByTagName("NativeMethods")
            
        nativeMethods=[]
        for nm in nms[0].getElementsByTagName("Method"):
            nativeMethods.append(Method.fromXML(nm))
            

        callingNativeMethods = []
        cnms = doc.getElementsByTagName("CallingNativeMethods")[0]           
        for cnm in cnms.childNodes:
            #print("Processing:")
            #print(cnm.getElementsByTagName("Name")[0].firstChild.nodeValue)
            callingNativeMethods.append(Method.fromXML(cnm))
            
        return JNI(path=path,
                    name=name,
                    nativeMethods=nativeMethods,
                    callingNativeMethods=callingNativeMethods)

def test():
    jni = JNI.load(r"S:\Desktop\tst\ActivityRecognitionHardware.java.xml")
    print(jni)
    
def convertParameter(x):
    params = []
    #if wanted can also be passed as given with
    #more information, but yet more is not needed
    for para in x.parameters:
        try:
            if ("model.Type" in str(type(para.type))):
                typ = str(para.type.name)
                if ("Name" in typ):
                    typ = str(para.type.name.value)
                                
                params.append(Parameter(typ=typ,
                                        name=str(para.variable.name)))
            else:
                params.append(Parameter(typ=str(para.type),
                                        name=str(para.variable.name)))
        except:
            cprint("JNI.py: convertParameter: NOT YET SUPPORTED PARAM:")
            cprint(type(para))
            cprint(para)
            cprint(type(para.type))
            cprint(para.type)
            exit()
    return params

def getNativeMethods(file):
    nativeMethods = []

    parser = jp.Parser()

    tree = parser.parse_file(file)
    if tree is None :
        cprint(tag+"getNativeMethods~Tree is None for: "+str(file))
        return nativeMethods

    try:
        for x in tree.type_declarations[0].body:
            if ('MethodDeclaration' in str(type(x))):
                if ('native' in x.modifiers):

                    params = convertParameter(x)

                    nativeMethod = Method(keywords=x.modifiers,
                                          name = x.name,
                                          parameter = params,
                                          calledNativeMethods=[])

                    nativeMethods.append(nativeMethod)
                    #print(nativeMethod)

    except Exception as e:
        cprint(tag + "getNativeMethods~" + str(tree))
        cprint(tag + "getNativeMethods~" + str(e) +"\nErrorEND")

    return nativeMethods

def addCalledNativeMethods(method,curr,nativeMethod):
    if (method is None):
        method = Method(keywords=curr.modifiers,
                        name=curr.name,
                        parameter=convertParameter(curr),
                        calledNativeMethods=[nativeMethod])
        return method
    else:
        method.addCalledNativeMethod(nativeMethod)
        return method                         
def recursiveNativeCallGraph():
    return

def checkForCalledNativeMethods(nativeMethods,piece,stmt,method):
    #check if calling native method:
    if ('MethodInvocation' in str(stmt)):
        if not any(natMet.getName() in str(stmt) for natMet in nativeMethods):
            return None
        else:
            #yet easy way, but mayb also store background info?
            spl = str(stmt).split('MethodInvocation')
            for p in spl:
                if ('name' in p):
                    nme = p.split("'")
                    nme = nme[1]
                    if any(nme in natMet.getName() for natMet in nativeMethods):
                        nativeMethod = Method(name=nme,
                                              info=stmt)                                              
                        method = addCalledNativeMethods(method,piece,nativeMethod)
          
    return method

def getNativeUsage(file,nativeMethods):
    nativeUsage=[]
    parser = jp.Parser()
    #print("File: "+file)
    tree = parser.parse_file(file)
    for x in tree.type_declarations[0].body:        
        method = None        
        if ('ConstructorDeclaration' in str(type(x))):            
            for b in x.block:
                method = checkForCalledNativeMethods(nativeMethods,x,b,method)                
                        
        if ('java_parser.plyj.model.MethodDeclaration' in str(type(x))):
            if not ('native' in x.modifiers):
                try:
                    for b in x.body:
                        method = checkForCalledNativeMethods(nativeMethods,x,b,method)
                except Exception as e:
                    cprint(tag+"getNativeUsage~Error on: "+str(x))
                    cprint(tag+"getNativeUsage~"+str(e))

        if not (method is None):
            nativeUsage.append(method)

    return nativeUsage
   
    

def generateJNI(file):
    spl = file.split(os.sep)

    nativeMethods = []
    callingNativeMethods = []
    try:
        nativeMethods=getNativeMethods(file)
    except Exception as e:
        print(tag+"ERR#1",e)

    try:
        #print(" Got "+str(len(nativeMethods))+" native Methods.")
        #print(nativeMethods)
        callingNativeMethods = getNativeUsage(file,nativeMethods)
    except Exception as e:
        print(tag+"ERR#2",e)

    try:
        return JNI(path=file,name=spl[len(spl)-1],nativeMethods=nativeMethods,
               callingNativeMethods=callingNativeMethods)
    except:
        return JNI(path=file,name="ERR",nativeMethods=nativeMethods,callingNativeMethods=callingNativeMethods)

#test()
