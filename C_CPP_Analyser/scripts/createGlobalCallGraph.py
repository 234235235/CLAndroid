import sys
import os
import threading
import traceback

from py2neo import Graph
from py2neo.data import Node, Relationship
    

BLUE="\033[38;5;20m"
RED="\033[38;5;9m"
GREEN="\033[38;5;82m"
CYAN="\033[38;5;14m"
ORANGE="\033[38;5;202m"
RESET="\033[0m"


tag=ORANGE+"[createGlobalCallGraph] "+RESET      

#ASSUMPTION NODE DOT FORMAT
#filename:: functionName:: [:: location]
#for filename EXT: filename:: functionName:: calledIn
def dot2Node(cg,line):
    spl = line.split(":::")
    fileName = spl[0].replace("\"","").strip()
    funcName = spl[1].replace("\"","").strip()

    #for filename EXT location is the location where this function is called
    #for others it is the path where to find the file
    location = None
    if (len(spl) > 2):
        location = spl[2].replace("\"","").replace("\\","/").strip()

    """
    if not (location == None):
        print("Node: "+funcName+" , file='"+fileName+"', location="+location)
    else:
        print("Node: "+funcName+" , file='"+fileName+"'")
    """
    
    available = cg.getNode("Function",properties={'srcFile' : fileName, 'funcName' : funcName, 'location' : location})
    if not(available == None):
        #print("Alrdy contained!")
        return available
    #print("ADDING NODE: "+funcName+", "+fileName+", "+location)
    return Node("Function", funcName=funcName,srcFile=fileName,location=location)


def dot2Relationship(cg,line):    
    spl = line.split("->")
    lhs = dot2Node(cg,spl[0])
    rhs = dot2Node(cg,spl[1])    
    return Relationship(lhs, "CALLS",rhs)


def load(path,cg,start,stop,total):
    curr=0
    printIntervall=1
    
    for file in os.listdir(path):
        if (os.path.isfile(os.path.join(path,file))):
            if not(os.path.splitext(file)[1] == ".dot"):
                #print(os.path.splitext(file)[1])
                continue

            if (curr < start):
                curr += 1
                continue

            if (((curr > stop) and (stop >= 0))or ((curr > total) and (total>=0))):
                return
            
            #print(tag+"Processing: "+CYAN+file+RESET+"...")
            with open(os.path.join(path,file), "r",errors="ignore") as f:
                #ASSUMPTION: DOT FILE NOT CORRUPTED AND EACH LINE CONTAINS 1 RELATION!
                for line in f:
                    if line in ["\n","\r\n"]:
                        continue
                    if ("digraph" in line):
                        continue
                    if (line == "}"):
                        continue
                    if not("->" in line):
                        try:
                            cg.addNode(dot2Node(cg,line))
                        except Exception as e:
                            print(tag+"ERROR: #load1",os.path.join(path,file))
                            print(tag+line)
                            print(e)
                    else:
                        try:
                            cg.addRelationship(dot2Relationship(cg,line))
                        except Exception as e:
                            print(tag + "ERROR: #load2", os.path.join(path, file))
                            print(tag + line)
                            print(e)


            curr += 1

            if (curr % printIntervall == 0):
                #cs = "["+str(curr)+"/"+str(stop)+"("+str(total)+")]"
                #print(tag+cs+"Processing: "+CYAN+file+RESET+"... "+GREEN+"DONE!"+RESET)
                print(tag+str(curr)+"/"+str(stop)+"["+str(total)+"] DONE!")


def merge(cg,idn,idm):
    q="MATCH (n:Function),(m:Function)"
    q+="WHERE id(n)="+str(idn)+" AND id(m)="+str(idm)+" "
    q+="OPTIONAL MATCH (n)-[s]->(succ) "
    q+="OPTIONAL MATCH (pre)-[r]->(n) "
    q+="DETACH DELETE (n) "
    q+="RETURN n,type(s) as s,id(succ) as succ,type(r) as r,id(pre) as pre,m as mergeTo"
    result = cg.getGraph().run(q)

    for res in result.data():
        preID = str(res["pre"])
        typ = res["r"]
        if not(typ == None or preID == None):
            q ="MATCH (pre),(m)"
            q+="WHERE id(pre)="+preID+" AND id(m)="+str(idm)+" "
            q+="MERGE (pre)-[:"+typ+"]-> (m)"
            #Isntead of merge could also use CREATE but then probably creates multiple time on
            #multiple runs (same as below with MERGE)
            cg.getGraph().run(q)

            sucID = str(res["succ"])
            typ = res["s"]
            if not (typ == None or sucID == None):
                q ="MATCH (succ),(m) "
                q+="WHERE id(succ)="+sucID+"id(m)="+str(idm)+" "
                q+="MERGE (m)-[:"+typ+"]-> (succ)"
                cg.getGraph().run(q)


    
def deleteDuplicates(cg):
    # delete duplicates

    q = """MATCH (n), (m)
               WHERE (
                       id(n) <> id(m)
               AND     n.srcFile = m.srcFile
               AND     n.location = m.location
               AND     n.funcName = m.funcName
                     )
               RETURN id(n) as idn, id(m) as idm
            """
    res = cg.getGraph().run(q)
    data = res.data()

    for n in data:
        idn = n["idn"]
        idm = n["idm"]
        merge(cg, idn, idm)

def doesIncl(cg,match):

    included = match["x"]
    implemented = match["y"]

    included_fname = included["location"]
    implemented_hname = implemented["srcFile"]

    if (".cpp" in implemented_hname):
        implemented_hname = implemented_hname.split(".cpp")[0]
    elif (".c" in implemented_hname):
        implemented_hname = implemented_hname.split(".c")[0]

    #implemented_hname.h od .hpp
    #if included_fname :INCLUDES implmented_hname then add candidate


    qS = "MATCH (n:File {name:\""+str(included_fname)+"\"}), "
    qh = "(m:File {name:\""+str(implemented_hname)+".h\"}), "
    qhpp = "(m:File {name:\"" + str(implemented_hname) + ".hpp\"}), "
    qE = "p = shortestPath( (n)-[r:INCLUDES*]->(m)) "
    qE += "RETURN count(p) > 0 as incl"

    hq = qS + qh + qE
    hppq = qS + qhpp + qE

    #print(hq)

    includes = cg.getGraph().run(hq).data()[0]["incl"]

    if (includes):
        return True

    includes = cg.getGraph().run(hppq).data()[0]["incl"]

    if (includes):
        return True

    return False



def link(cg): #(inclMap,cg,rootDir):
    skip = []
    print(tag+"Linking graphs...")
    not_changed = 0

    deleteDuplicates(cg)
    #maps together linked functions
    #e.g. func3 is implemented in tst.cpp which calles iFunc
    #     iFunc is implementend in tst2.cpp
    #     then we create / add the following entry to tst2.mp:
    #     iFunc: S:/.../tst.cpp|S:/.../bla.cpp
    
    linkMap = {}
    #return
    #TESTING
    #cg.addNode(Node("Function",funcName="iFunc",file="EXT",location=None))
    #n1 = Node("Function",funcName="bla",location="JNI_JNI_Helper_Dynamic.cpp",srcFile="EXT")
    #n2 = Node("Function",funcName="safe",location="S:/Uni/Master/MasterArbeit/CompeleteAnalysis/srcFiles/fullTest/native/helpers.cpp",srcFile="helpers.cpp")
    #cg.addNode(n1)
    #cg.addNode(n2)
    #cg.addRelationship(Relationship(n1,"CALLS",n2))


    queryS = """MATCH (x:Function), (y:Function)
                WHERE (x.srcFile='EXT' AND NOT y.srcFile='EXT') AND x.funcName=y.funcName               
             """

    queryE = """RETURN x,y,id(x) as IDx,id(y) as IDy
                ORDER BY id(y)
                
                LIMIT 1
             """
    
    while True:
        fq = queryS
        #fq += " AND NOT id(x) IN "+str(skip)+" "
        fq += " AND NOT id(y) IN "+str(skip)+" "
        fq += "\n"+queryE
        #print(fq)
        nodes = cg.getGraph().run(fq)
                
        if (nodes == None):
            break

        if (not_changed > 2):
            print(tag+RED+"link(): STUCK in while loop!"+RESET)
            print(nodes.data())
            break

        data=nodes.data()
        #print(data)
        if (len(data) < 1):
            break
        
        #if (not_changed > 0 and (not data[0]["IDx"] in skip)):            
        if (not_changed > 0 and (not data[0]["IDy"] in skip)):
            print("ADDING",data[0])
            #skip.append(data[0]["IDx"])
            skip.append(data[0]["IDy"])
            not_changed = 0
            
        not_changed += 1
       
        for i in range(len(data)-1):
            if not (data[i]["y"] == data[i+1]["y"]):
                print(tag+str(data[i]["y"])+"  "+str(data[i+1]["y"]))
                print(tag+RED+"link(): S.th went wrong #2"+RESET)
            
        #this IDy shoudl be the same for all nodes (as tested before)
        Idy = str(data[0]["IDy"])
        for n in data:
            node = n["x"]
            # merge x into y
            if (node["srcFile"] == "EXT"):
                #check if function is included from this file.

                shoulM = False
                try:
                    shouldM = doesIncl(cg,n)
                except Exception as ex:
                    print(tag+ORANGE+"link: Error during merging: "+RESET+str(ex))
                    print(traceback.format_exc())
                    print(tag+ORANGE+"Ignoring Error, continuing!"+RESET)

                if not (shouldM):
                    continue

                #print("MERGING: \n"+str(node)+"\n<>\n"+str(n["y"])+"\n")
                call = node
                origin = n["y"]
                src_file = origin["srcFile"]

                if not (src_file in linkMap.values()):
                    linkMap[src_file] = {}

                funcName = call["funcName"]
                if not (funcName in linkMap[src_file].values()):
                    linkMap[src_file][funcName] = []

                if not (call["location"] in linkMap[src_file][funcName]):
                    linkMap[src_file][funcName].append(call["location"])
                #print(linkMap)

                try:
                    merge(cg,n["IDx"],Idy)
                except Exception as e:
                    print(tag+"ERROR #link1 during merging!")
                    print(e)

                not_changed = 0
            else:
                print(tag+RED+"link(): S.th went wrong #1"+RESET)

    print(tag+"Linking Graphs... "+GREEN+"DONE!"+RESET)
    return linkMap

#crossCools = calls between differnt c files
#e.g. iFunc in tst2.cpp is vulnerable
#     iFunc gets called in line 9 in tst.cpp
#     then we link them together here and create an entry for this cross call
#     for the backwardsslicing.sc to work, as it cant connect with the neo4j database..
#     we simply use an txt format for transfering the result
#     in this case it would be:
#     filename: tst2.mp
#     1st line: iFunc:: (tst,9)
#     each function has 1 line, if it gets called from multiple files they can be concatenated
#     e.g. iFunc:: (tst,9)|(ttst,50)|(bla,23)
def writeToFiles(dst,linkMap):
    if not (os.path.exists(dst)):
        print(tag+RED+"Crosscall path does not exist: "+dst+"!"+RESET)
        return

    #print("DST: "+dst)
    #print("LINKMAP: "+str(linkMap))
    #print(tag+"TODO!")

    for file in linkMap.keys():
        dst_file, ext = os.path.splitext(file)
        dst_file = dst_file+".mp"
        with open(dst+dst_file,"w") as f:
            for func in linkMap[file].keys():
                f.write(func+"::: ")
                for call in linkMap[file][func]:
                    clean_call, ext = os.path.splitext(call)
                    if (linkMap[file][func][-1] == call):
                        f.write(clean_call)
                    else:
                        f.write(clean_call+"|")

                f.write("\n")



def main(dotPath,uri,user,password,crossCalls,modus="FULL",start=-1,stop=-1,total=-1):
    #print(tag+"Called with path: "+CYAN+dotPath+RESET)
    print(tag+"Modus: "+CYAN+modus+RESET)
    #print(uri)
    #print(user)
    #print(password)
    #print(crossCalls)
    #print(start,stop,total)

    cg = None
    
    try:
        cg = cgI.CallGraph(uri=uri,user=user,password=password)
        cg.getNode("tst")
    except Exception as e:
        print(tag+RED+"Connection to neo4j database could not be establisht!"+RESET)
        print(tag+RED+"Error:\n"+RESET+str(e))
        #print(tag+RED+e+RESET)
        return

    
    #loadGraphs(dotPath,cg)
    if not ("LOADED" in modus):
        load(dotPath,cg,start,stop,total)

    if "FULL" in modus:

        linkMap = link(cg)
        writeToFiles(crossCalls,linkMap)
    
    #cg.close()
    
#main("S:/Uni/Master/MasterArbeit/joernAnalysis/bwSlicing/out/dot/","S:/Uni/Master/MasterArbeit/joernAnalysis/bwSlicing/out/includes/")
if __name__ == '__main__':

    #for x in range(len(sys.argv)):
    #    print(x,sys.argv[x])

    if (len(sys.argv) < 7):
        print(tag+RED+"To less arguments..."+RESET)
        exit(0)

    #1 dotPath #2 database uri #3 username (database) #4 password (database) #5 crossCalls #6 path for callgraph.py #7modus #8 start #9 stop #10 total
    modus = "FULL"
    if (len(sys.argv) >= 8):
        modus = sys.argv[7]

    start = -1
    stop = -1
    total = -1
    if (len(sys.argv) >= 11):
        start = int(sys.argv[8])
        stop = int(sys.argv[9])
        total = int(sys.argv[10])

        if (stop > total):
            stop = total

    path = sys.argv[6]+"/Default/Callgraph.py"

    if sys.version_info >= (3,5):
        import importlib.util
        spec = importlib.util.spec_from_file_location("Callgraph.CallGraph",path)
        cgI = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cgI)

    elif sys.version_info >= (3,3):
        from importlib.machinery import SourceFileLoader
        cgI = SourceFileLoader("Callgraph.CallGraph",path).load_module()

    elif sys.version_info >=(2,0):
        import imp
        cgI = imp.load_source("Callgraph.CallGraph",path)
    else:
        print("Not supported python version: "+sys.version)
        
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],modus=modus,start=start,stop=stop,total=total)
