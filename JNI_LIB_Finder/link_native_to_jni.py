import os.path
import sys
import pandas as pd
import pathlib

path = pathlib.Path(__file__).parent.absolute().parent
sys.path.append(str(path))

from Default.Colors import Color
from JNI_LIB_Finder.JNI import JNI as JNI

tag = Color.ORANGE.value+"[link_native_to_jni] "+Color.RESET.value



def getContainedPerc(list1, list2):
    if (len(list1) < len(list2)):
        sw = list2
        list1 = list2
        list2 = sw

    matches = 0
    matching = False
    for x in range(len(list1)).__reversed__():
        if (list1[x] in list2):
            matches = matches + 1
            matching = True
        else:
            if (matching):
                break

    return matches/len(list2)


def link(row,lib_xml,jni_xml):
    print(tag+"Resolving "+Color.CYAN.value+row["srcFunc"]+Color.RESET.value)
    print(tag+"Location @: "+row["srcLoc"])

    jniFiles = []

    searchFileName = row["srcLoc"].split(os.path.sep)
    searchFileName = searchFileName[-1]
    
    
    searchFilePath = []
    
    while (True):
            
        searchFileName, ext = os.path.splitext(searchFileName)
        searchFileName = searchFileName + ".java"
        
        for file in os.listdir(jni_xml):
            name, ext = os.path.splitext(file)
            if (ext == ".xml"):
                if (name == searchFileName):
                    jniFiles.append(file)

        if (len(jniFiles) > 0 or not ("_" in searchFileName)):
            break

        searchFilePath.extend(searchFileName.split("_",1))
        searchFileName = searchFilePath[-1]
        




    matchedJni = None
    percentage = -1.0

    
    for f in jniFiles:
        jni = JNI.load(jni_xml + f)
        sfp = searchFilePath
        if (len(sfp) == 0):
            sfp.append(searchFileName)
        else:
            sfp[-1] = searchFileName

        curr_perc = getContainedPerc(jni.getPath().split(os.path.sep),sfp)

        if (curr_perc > percentage):
            percentage = curr_perc
            matchedJni = jni
            if (percentage == 1.0):
                break


    if (matchedJni == None):
        print(tag+Color.ORANGE.value+"Location could not be resolved."+Color.RESET.value)
        return None
    percentage = percentage * 100
    print(tag+Color.GREEN.value+"Resolved (%i%%)" % percentage+Color.RESET.value+"to: "+str(matchedJni.getPath()))
    return matchedJni


def main(csvFile, lib_xml, jni_xml):
    print(tag+"Trying to link native to JNI calls...")
    if not (os.path.isfile(csvFile)):
        print(tag+"File: '"+csvFile+"' does not exist!")
        return


    csv = pd.read_csv(csvFile)

    csv.rename(columns={"Function (Src)": "srcFunc","Function (Dst/Vul)":"dstFunc",
                        "Native Call":"jniCall","Dst/Vul Location":"dstLoc",
                        "Src Location":"srcLoc"},inplace=True)



    for idx,row in csv.iterrows():
        if (row["jniCall"] == "TODO"):
            res = link(row,lib_xml,jni_xml)
            if (res == None):
                row["jniCall"] = "None"
            else:
                csv.loc[idx,"jniCall"] = str(res.getPath())

    csvFile_resolved, ext = os.path.splitext(csvFile)
    csvFile_resolved = csvFile_resolved +"_resolved.csv"
    csv.to_csv(csvFile_resolved,index=False,header=True)
    print(tag+"Writing resolved summary to: "+Color.CYAN.value+csvFile_resolved+Color.RESET.value)
    print(tag + "Trying to link native to JNI calls... "+Color.GREEN.value+"DONE!"+Color.RESET.value)



#main("S:/Uni/Master/MasterArbeit/joernAnalysis/bwSlicing/out/summary.csv")

if __name__ == "__main__":
   
    if (len(sys.argv) < 4):
        print(tag+"To less arguments...")
        exit(0)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
        
