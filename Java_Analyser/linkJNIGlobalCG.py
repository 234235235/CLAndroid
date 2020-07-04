from py2neo import Graph
import pandas as pd
import sys

BLUE="\033[38;5;20m"
RED="\033[38;5;9m"
GREEN="\033[38;5;82m"
CYAN="\033[38;5;14m"
ORANGE="\033[38;5;202m"
RESET="\033[0m"


tag=ORANGE+"[linkJNIGlboalCG] "+RESET
def printDF(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth',100):
        print(df)
        
def getLinkMap(summary):
    res = []
    df = pd.read_csv(summary)
    #printDF(df.loc[df["jniCall"] != "None"])

    for idx, row in df.loc[df["jniCall"] != "None"].iterrows():      
        funcName = row["srcFunc"]
        res.append([funcName,funcName.split("_")[-1],row["jniCall"],row["srcLoc"]])


    return res

def link(linkMap,cg):

    for item in linkMap:       
        query = """MATCH (x:Function), (y:Function)
                   WHERE  x.funcName='"""+item[0]+"""' AND y.funcName='"""+item[1]+"""'
                          AND x.location='"""+item[3].replace("\\","/")+"""' AND y.location='"""+item[2].replace("\\","/")+"""'

                   MERGE (y)-[:JNI_CALL]-> (x)"""

        matches = cg.getGraph().run(query)

        
def main(summary,uri,user,password):
    cg = None
    
    try:
        cg = cgI.CallGraph(uri=uri,user=user,password=password)
        cg.getNode("tst")
    except Exception as e:
        print(tag+RED+"Connection to neo4j database could not be establisht!"+RESET)
        print(tag+RED+"Error:\n"+RESET+str(e))
        #print(tag+RED+e+RESET)
        return

    linkMap = getLinkMap(summary)

    link(linkMap,cg)



#u = "bolt://localhost:7687"
#us ="neo4j"
#pw = "kK0_1"
#s = r"S:\Uni\Master\MasterArbeit\CompleteAnalysis\Out\Java\summary.csv"
#main(s,u,us,pw)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("WRONG USAGE!")
        exit(0)
    path = sys.argv[5]+"/Default/Callgraph.py"
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

    
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

