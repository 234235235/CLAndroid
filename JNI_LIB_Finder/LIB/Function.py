import xml.etree.ElementTree as ET
from xml.dom import minidom

class Method:

    def __init__(self,name="",signature="",func="",includes=[],body=""):
        self.name = name
        self.signature = signature
        self.func = func
        self.includes = includes
        self.body=body
    

    def __repr__(self):
        return str(self)

    def __str__(self):
        strng = "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"

        strng += "Method               :"+self.name+"\n"
        strng += "Signature            :"+self.signature+"\n"
        strng += "Function declaration :"+self.func+"\n"
        strng += "Includes             :"+str(self.includes)+"\n"
        strng += "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"

        return strng


    def setName(self,name):
        self.name = name

    def setSignature(self,signature):
        self.signature = signature

    def setFunctionCall(self,func):
        self.func = func

    def setIncludes(self,includes):
        self.includes = includes

    def addInclude(self,include):
        self.includes.append(include)

    def getName(self):
        return self.name

    def getSignature(self):
        return self.signature

    def getFunctionCall(self):
        return self.func

    def getIncludes(self):
        return self.includes

    def toXML(self,obj):
        xml = ET.SubElement(obj,"Method")
        name = ET.SubElement(xml,"Name")
        signature = ET.SubElement(xml,"Signature")
        func = ET.SubElement(xml,"FunctionDeclaration")
        body = ET.SubElement(xml,"Body")
        #includes = ET.SubElement(xml,"Includes")

        name.text = self.name
        signature.text = self.signature
        func.text = self.func
        body.text = self.body

        ##TODO: INCLUDES

        return obj

    def fromXML(obj):
        name = ""
        signature = ""
        func = ""
        try:
            name = obj.getElementsByTagName("Name")[0].firstChild.nodeValue
            signature = obj.getElementsByTagName("Signature")[0].firstChild.nodeValue
            func = obj.getElementsByTagName("FunctionDeclaration")[0].firstChild.nodeValue
            body = obj.getElementsByTagName("Body")[0].firstChild.nodeValue
        except:
            pass

        return Method(name=name,
                      signature=signature,
                      func=func,body=body)
        
        
    
