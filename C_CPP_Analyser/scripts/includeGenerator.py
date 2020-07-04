from py2neo import Graph
from py2neo.data import Node,Relationship
import sys
import os
import time
from pathlib import Path
from createGlobalCallGraph import deleteDuplicates
import traceback
import datetime
import glob
import re
import ntpath

BLUE="\033[38;5;20m"
RED="\033[38;5;9m"
GREEN="\033[38;5;82m"
CYAN="\033[38;5;14m"
ORANGE="\033[38;5;202m"
RESET="\033[0m"


tag=ORANGE+"[includeGenerator] "+RESET
"""
path=r"S:/Uni/Master/MasterArbeit/CompleteAnalysis/Default/Callgraph.py"

import importlib.util
spec = importlib.util.spec_from_file_location("Callgraph.CallGraph",path)
cgI = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cgI)
"""
"""
lastChecked=datetime.datetime.now()
tolerance=20

def check(d="?"):
    now = datetime.datetime.now()
    diff=now - lastChecked
    lastChecked = now
    diff = diff.total_seconds()

    if (diff > tolerance):
        tprint(tag+"["+str(start)+"-"+str(stop)+"] Alive! Doing: "+str(d))
"""

def tprint(*strings):
    string=[str(s) for s in strings]
    print(" ".join(string))
    sys.stdout.flush()


def genInclude(srcDir,file,inclG):
    file = file.strip()
    srcDir = srcDir.strip()
    srcDir = srcDir.replace("\\","/")
    fullPath = os.path.join(srcDir,file)
    fullPath = fullPath.replace("\\","/")

    rootProps = {"name": file,"location":srcDir}

    available = inclG.getNode("File",properties=rootProps)

    if (available is None):
        node = Node("File",name=file,location=srcDir)
        inclG.addNode(node)


    with open(fullPath,"r",errors="ignore") as f:
        for line in f:
            if not(line.startswith("#")):
                continue

            if ("include" in line):
                line = line.strip()
                line = line.replace(" ","")

            if ("#include" in line):
                name = line.split("#include",1)[1]
                sysFile = False
                if ("<" in line and ">" in line):
                    name = name.split("<",1)[1].split(">",1)[0]
                    sysFile = True

                elif ("\"" in name):
                    name = name.split("\"",1)[1].split("\"")[0]

                dynamicPath = srcDir
                
                if ("\\" in name):
                    name = name.replace("\\","/")
                
                while ("//" in name):
                    name = name.replace("//","/")

                if ("/" in name):
                    p = name.split("/")
                    name = p[len(p)-1]
                    p = "/".join(p[:len(p)-1])
                    dynamicPath = str(Path(os.path.join(dynamicPath,p)).resolve())
                    dynamicPath = dynamicPath.replace("\\","/")

                if sysFile:
                    dynamicPath = "None"

                props = {"name": name,"location":dynamicPath}
                available = inclG.getNode("File",properties=props)

                if (available is None):
                    node = Node("File", name=name, location=dynamicPath)
                    inclG.addNode(node)


                pre = inclG.getNode("File",rootProps)
                succ = inclG.getNode("File",props)


                inclG.addRelationship(Relationship(pre,"INCLUDES",succ))

                







def loadIncludes(srcDir,inclG,start,stop,cur=0):
    printIntervall = 50
    totalTodo = stop - start
    #print(cur)
    #print(srcDir)
    if ((cur >=stop) and (stop != -1)):
        return cur
    try:
        for fod in os.listdir(srcDir):
            if (os.path.isdir(os.path.join(srcDir,fod))):
                cur = loadIncludes(os.path.join(srcDir,fod),inclG,start,stop,cur=cur)
            else:
                if (cur % printIntervall == 0 and cur != 0 and (cur - start) > start):
                    tprint(tag + "[" + str(start) + "-" + str(stop) + "] " + str(cur - start) + "/" + str(
                        totalTodo) + " DONE.")

                if (fod.endswith(".c") or fod.endswith(".cpp") or fod.endswith(".h") or fod.endswith(".hpp")):
                    if (start != -1 and stop != -1):
                        if (cur < start and start != -1):
                            cur += 1
                            continue
                        if (cur >= stop and stop != -1):
                            return cur

                    cur += 1
                    try:
                        #print("processing",fod)
                        genInclude(srcDir,fod,inclG)
                    except Exception as e:
                        tprint(tag+"ERROR"+srcDir,fod)
                        tprint(e)
                        traceback.print_exc()
                        sys.stdout.flush()
    
    except Exception as pd:
        tprint(tag+"ERROR",srcDir)
        tprint(pd)
        traceback.print_exc()
        sys.stdout.flush()

    return cur

def getMMN(compare,goal):
    """
    print(tag+"GMMN",len(compare))
    print(tag+"GOAL",goal)

    for x in compare:
        print(x)

    """

    idx = 0
    goal = goal.strip()
    while True:
        if (len(compare) <= 1):
            break
        if (idx > len(goal)):

            comparx = []
            for c in compare:
                cl = c["n"]["location"].replace("\\","/")
                while ("//" in cl):
                    cl = cl.replace("//","/")
                    
                if (len(cl.strip()) == len(goal.strip())):
                        comparx.append(c)
            compare = comparx
            if (len(compare) > 1):
                print(tag+"__getMMN__"+"multiple matches!")
                print(compare)
            break

        nxt = []
        for c in compare:
            cloc = c["n"]["location"].strip()
            cloc = cloc.replace("\\","/")
            while ("//" in cloc):
                cloc = cloc.replace("//","/")

            if (str(cloc[:idx]) == str(goal[:idx])):
                nxt.append(c)

            compare = nxt
            idx += 1

    if len(compare) > 0:
        #print("GMM RET",compare[0])
        return compare[0]
    #print("GMM RETN")
    return None

#getMMN([{"n": {"location": " /home/c01chbe/Build7_1/external/curl/include/curl"}},{"n": {"location": "/home/c01chbe/Build7_1/external/google-breakpad/src/third_party/curl"}}],
 #      "/home/c01chbe/Build7_1/external/curl/lib")

def processed(inclOut,app):
    #print("Checking",app)
    app = (app[0].strip(),app[1].strip())
    name = os.path.join(inclOut,app[0])+"*.incl"
    #print(name)
    files = glob.glob(name)
    #print("Candidates",files)
    pattern = "(\\\\|/)"+app[0]+"(_?)(\d*)\.incl"
    for f in files:
        match = re.search(pattern,f)
        if match:
            with open(f,"r",errors="ignore") as fl:
                if (app[1].strip() ==  fl.readlines()[0].strip()):
                    #print("found")
                    return True
    #print("Nope")
    return False

def derive(inclG,todo,done,inclOut):
    new_todo = []
    #tprint("####################")
    #tprint(todo)
    #tprint(done)
    #tprint("--------------------")
    for t in todo:
        t = (t[0].strip(),t[1].strip())
        try:
            if not (t in done):
                if not (processed(inclOut,t)):
                    done.append(t)
                else:
                    continue
            else:
                continue

            #tprint("CUR: ",t)
            cn = t[0]
            cloc = t[1]
            q = "MATCH (n) "
            q += "WHERE (n.name=\""+cn+".h\" OR n.name=\""+cn+".hpp\") "
            q += "RETURN n"
            res = inclG.getGraph().run(q).data()
            #tprint("CUR_RES",res)
            id = getMMN(res,cloc)
            #tprint("GETMMN RESULT",id)

            if (id is None):
                tprint(tag+"COULD_NOT_RESOLVE",cn,cloc,"\n",res)
                continue

            id = id["n"].identity

            q = "MATCH (m)-[:INCLUDES]->(n) "
            q+= "WHERE id(n)="+str(id)+" AND "
            q+= "(m.name ENDS WITH \".c\" OR m.name ENDS WITH \".cpp\") "
            q+= "RETURN m"

            res = inclG.getGraph().run(q).data()

            for r in res:
                r = r["m"]
                name = r["name"]
                if (name.endswith(".cpp")):
                    name = name.split(".cpp")[0]
                if (name.endswith(".c")):
                    name = name.split(".c")[0]
                loc = r["location"]
                app = (name.strip(),loc.strip())
                #if not processed druing this vulnerability
                if not (app in done):
                    #if not processed during backtracking other vulnerability
                    if not (processed(inclOut,app)):
                        new_todo.append(app)
        except Exception as e:
            tprint(tag+"ERROR: ",t)
            tprint(e)


    #tprint("####################")

    return new_todo,done

def writeIncludes(inclOut,done):
    for x in done:
        x = (x[0].strip(),x[1].strip())
        fname = os.path.join(inclOut, x[0]+ ".incl")
        i = 0
        while (os.path.isfile(fname)):
            fname = os.path.join(inclOut, x[0] + "_" + str(i) + ".incl")
            i += 1
        with open(fname, "w") as f:
            f.write(x[1])

def genIncludeList(inclG,inclOut,vulDir):
    if (vulDir is None):
        tprint(tag+"VULDIR NONE!")
        return []

    vuls = []
    for f in os.listdir(vulDir):
        if (f.endswith(".vul")):
            with open(vulDir + os.sep + f) as f:
                for line in f:
                    spl = line.split(";")
                    loc,fname = ntpath.split(spl[2])

                    loc = str(loc)
                    fname = str(fname)

                    if (fname.endswith(".cpp")):
                        fname = fname.split(".cpp")[0]
                    elif (fname.endswith(".c")):
                        fname = fname.split(".c")[0]

                    loc = loc.replace("\\", "/")
                    while (loc.endswith("/")):
                        loc = loc.split("/")
                        loc = loc[:len(loc)-1]
                        loc = "/".join(loc)

                    #print(loc)
                    #print(fname)
                    vuls.append((fname,loc))
    #done = []
    #tprint(vuls)
    #todo= vuls
    #while (len(todo)> 0):
        #todo,done = derive(inclG,todo,done)

    total = len(vuls)
    cur = 0
    maxListSize = 100
    printIntervall = 10
    
    for v in vuls:
        total_todo = [v]
        done = []
        while (len(total_todo) > 0):
            zw_total = len(total_todo)
            zw_cur = 0
            todo = total_todo
            total_todo = []
            for t in todo:
                todo_r,done = derive(inclG,[t],done,inclOut)
                total_todo.extend(todo_r)
                if (len(done) > maxListSize):
                    writeIncludes(inclOut,done)
                    done = []
                zw_cur += 1
                if (zw_cur % printIntervall == 0):
                    tprint(tag+"_subtask_"+str(zw_cur)+"/"+str(zw_total)+" DONE.")
        #print(done)
        writeIncludes(inclOut,done)
        cur += 1
        tprint(tag+str(cur)+"/"+str(total)+" DONE.")



    """
    for x in done:
        #improve cuz duplicates!!!!
        with open(os.path.join(inclOut,x[0]+".incl"),"w") as f:
            f.write("")
    """
def main(srcDir,inclOut,password,user="neo4j",uri="bolt://localhost:7771",start=-1,stop=-1,modus="FULL",vulDir=None,strategy="FAST"):
    """
    tprint("srcDir:",srcDir)
    tprint("vulDir:",vulDir)
    tprint("inclOut: ",inclOut)
    tprint("password: ",password),
    tprint("user: ",user)
    tprint("uri: ",uri)
    tprint("modus: ",modus)
    """
    if ("FULL" in strategy):
        tprint(tag+"Currently only FAST support, FULL is outdated.")
        tprint(tag+"Continuing with strategy FAST.")

    tprint(tag+"["+str(start)+"-"+str(stop)+"] Started!")
    #return
    if not (os.path.isdir(inclOut)):
        os.makedirs(inclOut)

    inclG = None

    try:
        inclG = cgI.CallGraph(uri=uri, user=user, password=password)
        inclG.getNode("tst")
    except Exception as e:
        tprint(tag + RED + "Connection to neo4j database could not be establisht!" + RESET)
        tprint(tag + RED + "Error:\n" + RESET + str(e))
        # tprint(tag+RED+e+RESET)
        return

    if ("FULL" in modus or "LOAD" in modus):
        loadIncludes(srcDir, inclG, start, stop)

    if (start != -1 and stop != -1):
        deleteDuplicates(inclG)

    if ("FULL" in modus or "GENINCL" in modus):
        if (vulDir is not None):
            genIncludeList(inclG, inclOut, vulDir)


    tprint(tag+"["+str(start)+"-"+str(stop)+"] DONE!")
#sd = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\srcFiles\fullTest"
#vd = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\C_CPP_Analyser"
#iO = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\C_CPP_Analyser\includes"
#pw = "kK0_1"

#main(sd,iO,pw)

if __name__ == '__main__':
    """
    for x in range(len(sys.argv)):
        tprint(x,sys.argv[x])
    """
    if (len(sys.argv) < 7):
        tprint(tag + RED + "To less arguments..." + RESET)
        exit(0)

    # 1 srcDir #2 inclOut #3 password  #4 user (database) #5 uri (database) #6 mainpath ##7 start ##8 stop ##9 modus ##10 vulDir #11strategy

    path = sys.argv[6] + "/Default/Callgraph.py"
    start = -1
    stop = -1

    if (len(sys.argv) >= 9):
        start=int(sys.argv[7])
        stop=int(sys.argv[8])

    modus = "FULL"
    if (len(sys.argv) >= 10):
        modus = sys.argv[9]

    vulDir=None
    if (len(sys.argv) >= 11):
        vulDir=sys.argv[10]

    strat="FAST"
    if (len(sys.argv) >= 12):
        strat=sys.argv[11]

    if sys.version_info >= (3, 5):
        import importlib.util
        spec = importlib.util.spec_from_file_location("Callgraph.CallGraph", path)
        cgI = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cgI)

    elif sys.version_info >= (3, 3):
        from importlib.machinery import SourceFileLoader
        cgI = SourceFileLoader("Callgraph.CallGraph", path).load_module()

    elif sys.version_info >= (2, 0):
        import imp
        cgI = imp.load_source("Callgraph.CallGraph", path)
    else:
        tprint("Not supported python version: " + sys.version)

    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],start=start,stop=stop,modus=modus,vulDir=vulDir,strategy=strat)
