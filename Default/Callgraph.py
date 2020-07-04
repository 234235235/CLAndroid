from py2neo import Graph
from py2neo.data import Node, Relationship 
#import os
from neo4j import (GraphDatabase, WRITE_ACCESS,)
import sys
import time
import random

def tprint(string):
    print(string)
    sys.stdout.flush()

class CallGraph:
    def __init__(self,uri,user,password):
        self._graph = Graph(uri,auth=(user,password))
        self.db = GraphDatabase.driver(uri,auth=(user,password))
        self.sess = self.db.session(default_access_mode=WRITE_ACCESS)
        self.user=user
        self.pw = password

    def __del__(self):
        self.sess.close()
        self.db.close()
        
    def addNode(self,node):
        if not (self._graph.exists(node)):      
            self._graph.create(node)
            
    #relationship as string!    
    def addNodeR(self,node_from,relationship,node_to):
        if not (self._graph.exists(Relationship(node_from,relationship,node_to))):
            self._graph.create(Relationship(node_from,relationship,node_to))
            
    #relationship as relationship type!
    def addRelationship(self,relationship):
        if not (self._graph.exists(relationship)):
            self._graph.create(relationship) 
       

    def merge(self,label):
        cg._graph.merge(label)
        
    def commit(self):
        self._tx.commit()

    def getGraph(self):
        return self._graph


    def getNode(self,node_label,properties=None,limit=1):
        #print("########################")
        q = "MATCH (n:"+node_label+") "
        if properties is not None:
            allNone = True
            for p in properties.values():
                if p is not None:
                    allNone = False
                    break

            if not allNone:
                q +="WHERE "
                nd = False
                for i in properties.items():
                    if i[1] is None:
                        continue
                    if nd:
                        q+=" AND "
                    q+= "n."+str(i[0])+ "='"+str(i[1]).replace("'","\'")+"'"
                    nd = True
                    

        q+= "RETURN (n) "
        if limit is not None:
            q+= "LIMIT "+str(limit)+";"
        else:
            q+=";"
            
        #print(q)
        #tprint("RUNNING QUERY:\n"+q)
        maxtries=10
        res2 = None
        #try avoid deadlocks
        for i in range(0,maxtries):
            try:
                res2 = self.sess.run(q)
            except:
                time.sleep(random.randrange(10))

        node = None
        try:
            res2 = iter(res2)
            res2= next(res2)
            n = res2.get("n")
            node = Node()
            node.identity = n.id
            node.update_labels(n.labels)
            for prop in n.items():
                node[prop[0]] = prop[1]           
            node.graph = self._graph
        except Exception as e:
            pass
        

        #tprint("QUERY:\n"+q+"\nSUCCESS\nRESULT: "+str(node))
        return node
       
