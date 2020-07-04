import java.io.{File => JFile}
import java.io.PrintWriter
import java.io.FileWriter

import scala.collection.mutable.ListBuffer
import scala.collection.mutable.Stack
import scala.collection.mutable.HashMap

import scala.io.Source

import io.shiftleft.codepropertygraph.generated.nodes
import io.shiftleft.semanticcpg.language.NodeSteps

var tag = "[backwardsSlicing] "

class Node{
	var name = "";
	var location= "";
	var isSink = false;
	var detailed = "";
	var None = false; //just for some / none bullshit
	
	override def toString: String = {
		var res = "##########\n"
		res += "Node:\n"
		res += "Name: "+name.toString+"\n"
		res += "##########\n"
		return res
	}
	
	def toString_offset(): String ={
		var res = "\n      ####Node###\n"
		res += "      ###Name: "+name.toString+"\n"
		res += "      ###Sink: "+isSink.toString+"\n"
		res += "      ###########\n"
		return res
	}
	
	def toDot(): String = {
		var res = "Name: "+name.toString+"\n"
		res += "Sink: "+isSink.toString+"\n"
		res += "Location: "+location.toString+"\n"
		res += "Details: \n"
		res += detailed
		return res;
	}
	override def equals(that: Any): Boolean = {
		that match {
			case that: Node => {
				if (name == that.name && location == that.location){
					return true;
				}
				return false;
			}
			
			case _ => return false;
		}
	}
		
	
}

class Tree{
	var vertices = Map[Node,ListBuffer[Node]]()
	
	def getRoots(): ListBuffer[Node] = {
		var roots = new ListBuffer[Node]()
	
		for (i <- vertices.keySet){				
			if (getPred(i,true).length == 0){
				roots.append(i)
			}
		}
		return roots
	}
	
	def getTails(): ListBuffer[Node] = {
		var tails = new ListBuffer[Node]()
		
		for (i <- vertices.keySet){
			if (vertices.get(i).isInstanceOf[Some[ListBuffer[Node]]]){
				if (vertices.get(i).head.length == 0){
					tails.append(i)
				}
			}
		}
		
		return tails
	}
	
	def getPred(n: Node, rec: Boolean): ListBuffer[Node] = {
		var pred = new ListBuffer[Node]()
		
		
		for (curr <- vertices.keySet){ //vulnerable
			//println(curr)
			var succs = vertices.get(curr) //vulnerable & between
			//println(succs)
			if (!succs.isEmpty){
				var s = succs.head  //[vulnerable,between]
				//println(s)
				if (s.contains(n)){		//if [vulnerable,between] contains (vulnerable)
					if (!(rec && (n.name.equals(curr.name)))){
						pred.append(curr)
					}
				}
			}
		}
		
		return pred
	}
	
	def addRoot(n: Node): Unit = {
		vertices = vertices.++(Map(n -> new ListBuffer[Node]))
		
	}
	def addNode(n: Node,parent: ListBuffer[Node]): Unit = {
		if (vertices.contains(n)){
			for (p <- parent){
				if (vertices.get(p) == None){
					addRoot(p)
				}
				if (!vertices.get(p).head.contains(n)){
					vertices.get(p).head.append(n)
				}
			}
		}
		else {
			vertices = vertices.++(Map(n -> new ListBuffer[Node]))
			for (p <- parent){
				if (vertices.get(p) == None){
					addRoot(p)
				}
				if (! vertices.get(p).head.contains(n)){
					vertices.get(p).head.append(n)
				}
			}
		}
	}
	
	def getNode(s: String): Node = {
		var res = vertices.keySet.find(i => i.name == s)
		if (!res.isEmpty){
			return res.head
		}
		
		//TODO: WITH SOME AND NON BUT SAME BUllSHIT
		var ret = new Node()
		ret.None = true;
		return ret
	}
	
	
	def merge(t: Tree): Unit =  {		
		var roots = t.getRoots
		var tails = getTails
		
		for (n <- t.getNodes){
			//println("WTF: "+t.getPred(n))
			addNode(n,t.getPred(n,false))
		}		
		
		for (r <- tails){
			if (vertices.get(r).isInstanceOf[Some[ListBuffer[Node]]]){
				vertices.get(r).head.appendAll(roots)
			}
		}		
		
	}
	
	def getNodes(): Set[Node] = {
		return vertices.keySet
	}
	
	override def toString: String = {
		var res = "#####\nTree:\n"
		
		for (it <- vertices.keySet){
			var succs = vertices.get(it)
			res += it.name.toString+" -->"
			for (succ <- succs.head){
				res += succ.toString_offset()
				res += "   -->\n"
			}
			if (succs.head.length == 0){
				res += " LEAF"
			}
			res += "\n"
		}
		
		
		
		return res
	
	}
	
	def toDot: String = {
		var res = "digraph Tree {\n"
		
		for (it <- vertices.keySet){
			if (!vertices.get(it).isEmpty){
				for (succ <- vertices.get(it).head){
					res += "\""+it.toDot.replace("\"","\\")+"\" -> \""+succ.toDot.replace("\"","\\")+"\";\n";
				}
			}
		}
		
		res += "\n}"
		return res;	
	}
}


//TODO: with id?
def getCallees(func: String): Steps[Method] = {
	
	return cpg.method.filter(_.callOut.name(func));
}




//def findSrc_V2(src: NodeSteps[nodes.TrackingPoint], snk: NodeSteps[nodes.TrackingPoint]): Tree = {
def findSrc_V2[A](srcFuck: A, snkFuck: A): Tree = {
	
	//JA, geth best. eleganter i.e. [A <: nodes.TrackingPoint](src: NodeSteps[A]) od so aehnlich,
	//GEHT ABER IRGENDWIE NICHT WISOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO?!?!??!?!	

	var src = srcFuck.asInstanceOf[NodeSteps[nodes.TrackingPoint]]
	var snk = snkFuck.asInstanceOf[NodeSteps[nodes.TrackingPoint]]
	
	var ftag = "[findSrc_V2] "
	var t = new Tree()
	
	var fst = snk.reachableByFlows(src).p	

	var r = new Node();
	
	
	
	
	
	r.name = src.clone.method.name.head
	r.location = src.clone.head.location.filename
	r.detailed = fst.toString
	t.addRoot(r)
	println(ftag+"Root added: "+r)
	println(ftag+"curr tree: "+t)
	
	
	//no data flow from vul nach parameter
	if (fst.isEmpty){
		println(ftag+"Returning tree: "+t)
		return t;
	}
	

	
	var todo = Stack(src.clone.method.name.head) //vulnerable
	var done = ListBuffer[String]()	
	
	while (!todo.isEmpty){
		var curr = todo.pop		//vulnerable
		done.append(curr)
		println(ftag+"Curr: "+curr)
		var srcc = getCallees(curr).parameter //vulnerable (rec) //main 
		var snkk = getCallees(curr).callOut.name(curr).argument //char //int
		
		var ids = new ListBuffer[String](); 
		
		println("IDS")
		
		var par = t.getNode(curr)
		
		for (c <- getCallees(curr).l){
			println(c)
			if (c.parameter.isEmpty){
				var nn = new Node()
				nn.name = c.name
				nn.location = c.location.filename
				nn.isSink = true
				t.addNode(nn,new ListBuffer[Node]().append(par))
			}
		}
		
		for (s <- srcc.clone.l){
			println(s)
			ids.append(s.getId.toString)
			println(s.getId.toString)
		}
			
		
		
		for (id <- ids){
			println("Processing"+id+" "+srcc.clone.id(id).method.name.head)
			
			var rs = snkk.reachableByFlows(srcc.clone.id(id)).p
			var n = t.getNode(srcc.clone.id(id).method.name.head)
			if (n.None){
				n = new Node()
				n.name = srcc.clone.id(id).method.name.head
				n.location = srcc.clone.location.head.filename
			}
			
			//var par = t.getNode(curr)
			
			println(ftag+"ID: "+id+" ("+srcc.clone.id(id).method.name.head+" -> "+curr+" reachable: "+rs.isEmpty.toString+")")
			
			if (!rs.isEmpty){
				var psh = srcc.clone.id(id).method.name.head
				if (! done.contains(psh)){
					todo.push(srcc.clone.id(id).method.name.head)
				}
				n.detailed = n.detailed+ "\n"+rs.toString
				println(ftag+rs)
			} else{
				n.isSink = true
				n.detailed = n.detailed +"\n"
				
				var call = getCallees(curr).callOut.name(curr).l.filter(in => in.method.name == srcc.clone.id(id).method.name.head)
				
				for (c <- call){
					n.detailed = n.detailed + "Call: "+c.code.toString+" lineNbr: "+c.lineNumber.head.toString+"\n"
				}
			}
			
			t.addNode(n,new ListBuffer[Node]().append(par))
			println(ftag+"tree atm: "+t)
		}		
	
	}	
	return t

}


def backWardsSlice(func: String, snkLine: Int= -1): Tree = {
	//todo
	println("backWardsSlice called with: "+func+","+snkLine)
	
	var tree = new Tree()	
		
	if (snkLine >= 0){
		var snk = cpg.call.lineNumber(snkLine).argument
		var src = cpg.method.name(cpg.call.lineNumber(snkLine).method.name.head).parameter		
		tree = findSrc_V2(src,snk)
	}
	else {
		var snk = cpg.method.name(func).cfgLast
		var src = cpg.method.name(func).parameter
		tree = findSrc_V2(src,snk)
	}	
	
	return tree; 
}

//HashMap[funcName,extern function calls]
//e.g. iFunc,[(tstcpp,3)] meaning iFunc in cpgFile gets called from tstcpp in line 3

//ed def getCrossCalls(crossCalls: String,cpgPath: String,cpgName: String): HashMap[String,ListBuffer[(String,Integer)]] = {
def getCrossCalls(crossCalls: String,cpgPath: String,cpgName: String): HashMap[String,ListBuffer[String]] = {
	
	//ed var res = new HashMap[String,ListBuffer[(String,Integer)]]()
	var res = new HashMap[String,ListBuffer[String]]()	
	
	var file = new JFile(crossCalls+cpgName+".mp")
	println("looking for file: "+file.toString)
	if (!file.exists){
		return res
	}
	
	for (line <- Source.fromFile(crossCalls+cpgName+".mp").getLines()){
		var fName = line.split(":::").apply(0)
		var calls = line.split(":::").apply(1)
		
		//println("fname: "+fName)
		//println("calls: "+calls)
		
		//ed var callList = new ListBuffer[(String,Integer)]()
		var callList = new ListBuffer[String]()
		
		for (call <- calls.split("\\|")){
			var ct = call.trim()			
			//ed var f = ct.split(",").apply(0).split("\\(").apply(1)
			//ed var l = ct.split(",").apply(1).split("\\)").apply(0).trim.toInt			
			println("appending: "+ct)
			//ed callList.append((f,l))
			callList.append(ct)
		}
		
		res.put(fName,callList)
	}
	
	
	
	
	return res
}


@main def main(cpgPath: String="None",cpgName: String="None",func: String="None", lnNbrStr: String="None", crossCalls: String="None", outFile: String="None",csvFile: String="None"): Unit = {

	
	println("\n\nCPGPATH: "+cpgPath)
	println("cpgNAME: "+cpgName)
	
	var cpgEnding = ".bin.zip"
	
	var res = "";
	var csv = ""; 
	var globalTree = new Tree();

	//TODO: variable aka lineNumber aka unknown? 
	
	var todo = Stack[(String,String,Int)]()
	if (lnNbrStr == "None"){
		todo.push((cpgName,func,-1))
	} else{
		var lnNbr = lnNbrStr.toInt
		todo.push((cpgName,func,lnNbr))
	}
	
	
	while (!todo.isEmpty){	
		
		
		var curr = todo.pop()
		println(curr)
		var curr_Cpg = curr._1
		var curr_Func = curr._2
		var curr_LNBR = curr._3
		
		if (!new JFile(cpgPath+curr_Cpg+cpgEnding).exists()){
			println(tag+"WARNING: File: "+curr_Cpg+" does not exist!")
		}
		else {
			if (curr_Cpg!="None"){
				loadCpg(cpgPath+curr_Cpg+cpgEnding);
				println("CPG LOADED: "+cpgPath+curr_Cpg+cpgEnding)
				
			}
			
			//naja.. es funktioniert... aber mal schauen ob noch schöner geht.
			if (curr_LNBR == -2){
				var vul_func = curr_Func
				curr_Func = ""
				var first = true
				for (cll <- cpg.call.name(vul_func).l){
					if (first){
						curr_LNBR = cll.lineNumber.head
						first = false
					}
					else{
						todo.push((curr_Cpg,"",cll.lineNumber.head))
						println("PUSHING#2: ("+curr_Cpg+",  ,"+cll.lineNumber.head+")")
					}
				}
			}
			
			
			var bRes = backWardsSlice(curr_Func,curr_LNBR);
			println("Got as bwslice result (local):\n"+bRes.toString)
			globalTree.merge(bRes) //globalTree.merge(bRes)		

			//println(crossCalls)
			//println(cpgPath)
			//println(curr_Cpg)
			var mp = getCrossCalls(crossCalls,cpgPath,curr_Cpg)
			
			for (n <- bRes.getNodes){	
				//check for global callees (in global callgraph)
				//add those!
				
				if (mp.get(n.name) != None){
					for (outC <- mp.get(n.name).head){
						//ed todo.push((outC._1,"",outC._2))
						todo.push((outC,n.name,-2))						
					}	
				}		
			}			
		}
	}
	
	println("RESULT TREE:")
	println(globalTree.toString)
	
	res += globalTree.toDot
	

	if (res != ""){
		if (outFile != "None"){	
			val writer = new PrintWriter(new JFile(outFile));
			writer.write(res.toString());
			writer.close();
		}
	}	
		
	
	
	var root = globalTree.getRoots.head	

	for (n <- globalTree.vertices.keySet){
		//if (n.isSink == true){
		//TODO: Only if function accessible from outside by another func!
		csv += n.name + "," + root.name +"," +"TODO"+ "," +root.location.toString+","+n.location+"\n"
		//}
	}
	
	
	if (csv != ""){
		if (csvFile != "None"){
			val csvF = new JFile(csvFile);			
			if (!csvF.exists()){				
				csv = "Function (Src),Function (Dst/Vul),Native Call,Dst/Vul Location,Src Location\n" + csv;
			}
			val wr = new FileWriter(csvF,true);
			wr.write(csv.toString());
			wr.close();
		}
	}
	
	return 
}
