import xml.etree.ElementTree as ET
class Method:
    #parameter = list of class Parameter
    def __init__(self,keywords=[],name="",parameter=[],calledNativeMethods=[],info=None):
        self.keywords = keywords
        self.name = name
        self.parameter = parameter
        self.calledNativeMethods = calledNativeMethods
        self.info = info

    def setKeywords(self,keywords):
        self.keywords = keywords

    def setName(self,name):
        self.name = name

    def setParameter(self,parameter):
        self.parameter = parameter

    def setInfo(self,info):
        self.info = info
        
    def addParameter(self,param):
        self.parameter.append(param)

    def setCalledNativeMethods(self,cnm):
        self.calledNativeMethods = cnm

    def addCalledNativeMethod(self,cnm):
        self.calledNativeMethods.append(cnm)

    def getInfo(self):
        return self.info

    def getKeywords(self):
        return self.keywords

    def getName(self):
        return self.name

    def getParameter(self):
        return self.parameter

    def getCalledNativeMethods(self):
        return self.calledNativeMethods

    def toXML(self,obj):
        #print(ET.tostring(obj))
        xml = ET.SubElement(obj,"Method")
        name = ET.SubElement(xml,"Name")
        keywords = ET.SubElement(xml,"Keywords")
        parameter = ET.SubElement(xml,"Parameter")
        calledNativeMethods = ET.SubElement(xml,"CalledNativeMethods")
        info = ET.SubElement(xml,"Info")

        name.text = self.name
        keywords.text = str(self.keywords)

        for para in self.parameter:
            paramter = para.toXML(parameter)        

        for nm in self.calledNativeMethods:
            #short version
            sub = ET.SubElement(calledNativeMethods,"Method")
            n = ET.SubElement(sub,"Name")
            i = ET.SubElement(sub,"Info")
            n.text = nm.getName()
            i.text = str(nm.getInfo())

        info.text = str(self.info)

        #print(ET.tostring(obj))
        return obj
    
    def fromXML(obj):
        name = obj.getElementsByTagName("Name")[0].firstChild.nodeValue
        kws = obj.getElementsByTagName("Keywords")[0].firstChild.nodeValue
        keywords = []
        kws = kws.replace("'","")
        kws = kws.replace("[","")
        kws = kws.replace("]","")
        kws = kws.split(",")
        for kw in kws:
            keywords.append(kw.strip())

        para = obj.getElementsByTagName("Parameter")
        parameter =[]
        for p in para:
            res = Parameter.fromXML(p)
            if not (res is None):
                parameter.append(Parameter.fromXML(p))

        calledNativeMethods = []

        
        nms = obj.getElementsByTagName("CalledNativeMethods")[0]

        if not (nms is None):
            for nm in nms.getElementsByTagName("Method"):
                nm_name = nm.getElementsByTagName("Name")[0].firstChild.nodeValue
                nm_info = nm.getElementsByTagName("Info")[0].firstChild.nodeValue
                calledNativeMethods.append(Method(name=nm_name,
                                                  info=nm_info))

        info = obj.getElementsByTagName("Info")[0].firstChild.nodeValue

        if (info == "None"):
            info = None
        
        return Method(keywords=keywords,
                      name=name,
                      parameter=parameter,
                      calledNativeMethods=calledNativeMethods,
                      info=info)
        
        
    def __repr__(self):
        return str(self)

    def __str__(self):
        strng =  ("-------------------------------------------------------------\n")
        strng += ("Method              :"+self.name+"\n")
        strng += ("Keywords            :"+str(self.keywords)+"\n")
        strng += ("Parameter           :"+str(self.parameter)+"\n")
        #kurzer string
        strng += ("calledNativeMethods :")
        i = 0
        for nm in self.calledNativeMethods:
            if (i == 0):
                strng += nm.getName()
                i += 1
            else:
                strng += ", "+nm.getName()
                
        strng += "\n"
        #Ausfuerlicher string
        """
        strng += ("calledNativeMethods :\n")
        for nm in self.calledNativeMethods:
            strng += "      "+"................\n"
            strng += "      "+nm.getName()+"\n"
            strng += "      "+str(nm.getInfo())+"\n"
            strng += "      "+"................\n"
        strng += "\n"
        """
        strng += ("Info:               :"+str(self.info)+"\n")
        strng += ("-------------------------------------------------------------\n")
        return strng
        
    
class Parameter:

    def __init__(self,typ="",name=""):
        self.typ = typ
        self.name = name

    def __str__(self):
        return (self.typ+" "+self.name)
    def __repr__(self):
        return (self.typ+" "+self.name)
    
    def setTyp(self,typ):
        self.typ = typ

    def setName(self,name):
        self.name = name

    def getTyp(self):
        return self.typ

    def getName(self):
        return self.name

    def toXML(self,obj):
        xml = ET.SubElement(obj,"Parameter")
        name = ET.SubElement(xml,"Name")
        typ = ET.SubElement(xml,"Type")

        name.text = self.name
        typ.text = self.typ

        return obj

    def fromXML(obj):
        try:
            name = obj.getElementsByTagName("Name")[0].firstChild.nodeValue
            typ = obj.getElementsByTagName("Type")[0].firstChild.nodeValue
        
            return Parameter(name=name,typ=typ)
        except:
            return None


    
        
