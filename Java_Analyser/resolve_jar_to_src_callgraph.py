import pandas as pd
import os
import re
import sys
tag = "[resolve_jar_to_src_callgraph]"
def getMap(summary):
    df = pd.read_csv(summary)
    mp = df.loc[(df["jniCall"] != "None") & (df["Jar"] != "None"),["jniCall","Jar"]]
    
    return mp

def printDF(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth',100):
        print(df)

def processStr(string,mp):
    #print("PROCESSING: ")
    #print(string)
    
    res = string.split(" ")
    res = list(filter(None,res))
    lst = []
    for e in res:
        if ".jar" in e:
            #print("JAR FOUND: "+e)
            ls = e.split(".jar")[0]+".jar"
            rs = e.split(".jar")[1]
            #print("LF: "+ls)
            lst = mp.loc[mp["Jar"] == ls,"jniCall"].unique().tolist()
            #print("LIST: "+str(lst))



    subclass=False
    search = res[0]
    if ("\"" in search):
        search = search.replace("\"","")
        
    #print("s b4: "+search)
    if ("$" in search):
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        #print(tag+"Subclass seemd to be used")
        #print(tag+"Original name: "+str(search))
        search = search.split("$",1)[0]+".java"
        #print(tag+"Edited to: "+str(search))
        subclass = True

    #print("\nSUBCLASS: "+str(subclass)+"\n")
    for item in lst:
        #print("RES: "+str(res))
        name = re.split("\\\\|\\|//|/", item)
        path = name[:len(name)-1]
        name = name[-1]
        if ("$" in name):
            #print(tag+"Subclass seemd to be used")
            #print(tag+"Original name: "+str(name))
            name = name.split("$",1)[0]
            #print(tag+"Edited to: "+str(name))

        #print("I: ",item)
        #print("N: "+name)
        #print("S: "+search)
        
        if name in search:            
            res[2]="/".join(path)+"/"+name+"\""
            #print("CHANGED")
         
        elif subclass:
            #BUGFIX
            #compare classes
            #BUT REAL FIX: Edit bws.jar!
            #~backTrackLocal~ WARNING: Currently only
            #supported initial comparison by function names,...
            #print("P: ",path)
            p = list(filter(None,path))
            sp = list(filter(None,re.split("\\\\|\\|//|/", search)))
            sp = sp[:len(sp)-1]
            match = True
            for idx in range(1,len(sp)+1):
                if (len(p) - idx >= 0):
                    #print("COMPARING")
                    #print(p[len(p)-idx])
                    #print("?=?")
                    #print(sp[len(sp)-idx])
                    if (p[len(p)-idx] != sp[len(sp)-idx]):
                        #print("FALSE")
                        match = False
                        break
                    #print("TRUE")

            if (match):
                res[2]="/".join(path)+"/"+name+"\""
                
                
                
                    
                
        
    res = " ".join(res)
    #if (res != string):
    #    print("CHANGED: ")
    #    print(res)
    return res

def processLine(line,mp):
    newLine = ""
    if "->" in line:
        ls = line.split("->")[0]
        rs = line.split("->")[1]
        newLine = processStr(ls,mp)+" -> "+processStr(rs,mp)

    else:
        newLine = processStr(line,mp)

    return newLine

def processCG(cgDir,file,mp):
    content = ""
    #print(file)
    with open(cgDir+os.path.sep+file,"r") as f:
        for line in f.readlines():
            #print("b4: "+line)
            if ".jar" in line:
                nl =  processLine(line,mp)+"\n"
                content += nl
                #print("after: "+nl)
            else:
                content+=line
                #print("after: (same)")

    
    with open(cgDir+os.path.sep+file,"w") as f:
        f.write(content)
    
    
    #print(content)


def editCG(mp,cgDir):
    for file in os.listdir(cgDir):
        if file.endswith(".dot"):
            #print(file+":\n")
            processCG(cgDir,file,mp)
            


def main(summary,cgDir):
    mp = getMap(summary)    
    editCG(mp,cgDir)
    



#summ=r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\Java\summary.csv"
#cgDir=r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\Java\LocalBackTrackCGs"

#main(summ,cgDir)

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("WRONG USAGE!")
        exit(0)

    summary = sys.argv[1]+"summary.csv"
    cgDir = sys.argv[1]+"LocalBackTrackCGs"


    if (os.path.exists(cgDir)):
        if (os.path.isfile(summary)):
            main(summary,cgDir)
        else:
            print(tag+"SKIPPING DUE TO MISSING SUMMARY FILE!")
    else:
        print(tag+"SKIPPING DUE TO NO OUTPUT OF LOCALBACKTRACKS!")
            
