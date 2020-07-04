import pandas as pd
import os
import re
import zipfile
#from unrar import rarfile
import sys
from io import BytesIO
import ntpath

def readSum(summary):
    df = pd.read_csv(summary)
    try:
        df.insert(loc=3,column="Jar",value="None")
    except:
        pass

    try:
        df.insert(loc=4,column="perc",value=0)
    except:
        pass


    return df

def delSameDirs(path1, path2):
    path1 = list(filter(None,path1))
    path2 = list(filter(None,path2))

    minlen = min(len(path1), len(path2))


    sameIdx = 0
    for i in range(0,minlen):
        if (path1[i] != path2[i]):
            break

        sameIdx = i

    return path1[sameIdx+1:]

def getPercentage(name,path,matchStr,jarParentDir):

    matchStrS = re.split("\\\\|\\|//|/", matchStr)
    if not (os.path.splitext(matchStrS[-1])[0] == name ):
        return 0


    diff = delSameDirs(path,re.split("\\\\|\\|//|/",jarParentDir))
    matchStrS = matchStrS[:len(matchStrS)-1]

    diff2 = delSameDirs(diff,matchStrS)
    perc = len(diff2) / len(diff)

    return int(perc*100)

def clean(list):
    res = []
    for item in list:
        done = False
        for r in res:
            if r[0] == item[0]:
               if r[2] < item[2]:
                    res.remove(r)
                    res.append(item)
               done = True

        if not (done):
            res.append(item)


    return res

def updateMatchesDex(todo,file,df,parentDir):
    #print("updateMatchesDex")
    for x in todo:
        if x.endswith("/") or x.endswith("\\"):
            while (x.endswith("/") or x.endswith("\\")):
                x = x[:len(x)-1]

        detect = ntpath.basename(x).split(".java")[0]
        path = ntpath.split(x)[0]
        path = re.split("\\\\|\\|//|/", path)
        detectb = bytes(detect,"utf-8")
        res = ""
        #print("NAME",detect)
        #print("PATH",path)
        with open(file,"rb") as f:
            for line in f.readlines():
                if (detectb in line):
                    namepath = str(line).split(";")
                    for item in namepath:
                        item = str(item)
                        if (detect in item) and ("L" in item):
                            res = item
                            if ("/"+detect in item):
                                try:
                                    res = res.split("L",1)[1]
                                except:
                                    pass
        if (res != ""):
            perc = getPercentage(detect,path,res,parentDir)

            if (df.loc[df["jniCall"] == x, "perc"].iloc[0] < perc):
                file = "/".join(re.split("\\\\|\\|//|/", file))
                df.loc[df["jniCall"] == item, "Jar"] = file
                df.loc[df["jniCall"] == item, "perc"] = perc
    return df
                    

def updateMatches(todo,matchStr,file,df,jarParentDir):
    #print("updateMatches")
    #print("TODO",todo)
    #print("MATCHSTR",matchStr)
    #print(file)
    for item in todo:
        xsplit = re.split("\\\\|\\|//|/", item)
        name = os.path.splitext(xsplit[-1])[0]
        path = xsplit[:len(xsplit)-1]
        #print("NAME",name)
        #print("PATH",path)
        if name in matchStr:
            perc = getPercentage(name,path,matchStr,jarParentDir)

            if (df.loc[df["jniCall"] == item, "perc"].iloc[0] < perc):
                file = "/".join(re.split("\\\\|\\|//|/", file))
                df.loc[df["jniCall"] == item, "Jar"] = file
                df.loc[df["jniCall"] == item, "perc"] = perc

    return df

def searchZipLike(zipf,endings,todo,df,jarParentDir,parentZip=None):
    #print("SZL")
    #print(zipf)
    #print(type(zipf))
    #print(todo)

    if (isinstance(zipf,BytesIO)):
        zf = zipfile.ZipFile(zipf)
    else:
        zf = zipfile.ZipFile(zipf,"r")
    try:
        for name in zf.namelist():
            #print(name)
            f, ext = os.path.splitext(name)
            if (ext in endings):
                zfdata = BytesIO(zf.read(name))
                searchZipLike(zfdata,endings,todo,df,jarParentDir,zipf)
            if (ext == ".class"):
                #print("------------------")
                #print(zipf)
                #print(name)
                #print(orig)
                #print("------------------")
                updateMatches(todo,name,parentZip,df,jarParentDir)
    except Exception as e:
        print("Exception during crawling through ziplike object: \n"+e)
        print(zipf)
        print(type(zipf))

    finally:
        zf.close()


def linkToJar(df,jarParentDir):

    todo = df.loc[df["jniCall"] != "None"]
    todo = todo["jniCall"].tolist()

    zipEndings =[".jar",".dex",".jack",".jayce",".zip"]
    olddf = df

    for root, dirs, files in os.walk(jarParentDir):
        for file in files:
            #if file.endswith(".jar"):
            f, ends = os.path.splitext(file)
            #if (ends == ".rar"):
            #    print("NOOOOO rar file well, i screwed.")
            #if ends in zipEndings:
            #    searchZipLike(root+os.sep+file,zipEndings,todo,df,jarParentDir)
            if (file.endswith(".dex")):
                continue
                #df = updateMatchesDex(todo,os.path.join(root,file),df,jarParentDir)
            elif (file.endswith(".jar")):
                try:
                    if (os.path.islink(root+os.path.sep+file)):
                        continue
                    jf = zipfile.ZipFile(root+os.path.sep+file,"r")
                    try:
                        lst = jf.infolist()
                        for zi in lst:
                            fn = zi.filename
                            if fn.endswith('.class'):
                                df = updateMatches(todo,fn,root+os.path.sep+file,df,jarParentDir)

                    finally:
                        jf.close()
                except Exception as e:
                    print("ERR#6",e)
                    print(root+os.path.sep+file)
        
        #print("Current df")
        #print(df)
                
    return df

def writeJavaBacktracks(df,outFolder):

    jars = df.loc[df["Jar"] != "None","Jar"].unique()
    dict = {}

    for jar in jars:
        for idx, row in df.loc[df["Jar"] == jar].iterrows():
            functionName=row["srcFunc"].split("_")[-1]
            if (dict.__contains__(jar)):
                dict[jar].append(functionName)
            else:
                dict[jar] = [functionName]

    with open(outFolder+os.path.sep+"todo.txt","w") as f:
        for entry in dict:
            bt = (" | ").join(set(dict[entry]))
            entry = "/".join(re.split("\\\\|\\|//|/",entry))
            f.write(entry+"; "+bt+"\n")

    #df.loc[df["Jar"] != "None","Jar"].tolist():


    #f.write(item)

    return

def main(summary,jarParentDir,javaAnalyserOut):
    javaAnalyserOut = re.split("\\\\|\\|//|/",javaAnalyserOut)
    javaAnalyserOut = os.path.sep.join(javaAnalyserOut)
    df = readSum(summary)
    df = linkToJar(df,jarParentDir)
    if not (os.path.exists(javaAnalyserOut)):
        os.makedirs(javaAnalyserOut)

    df.to_csv(javaAnalyserOut+os.path.sep+"summary.csv",columns=["srcFunc","dstFunc","jniCall","Jar","dstLoc","srcLoc"])

    writeJavaBacktracks(df,javaAnalyserOut)


#jarDir = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\srcFiles\fullTest"
#sumDir = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\C_CPP_Analyser\summary_resolved.csv"
#javaAnalyserOut = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\Java_Analyser"
#main(sumDir, jarDir,javaAnalyserOut)

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("WRONG USAGE!")
    else:
        main(sys.argv[1],sys.argv[2],sys.argv[3])

