import scala.collection.mutable.ListBuffer;

import java.io.{File => JFile}
import java.io.PrintWriter
import java.io.FileWriter


/* ########################################################   Bufferoverflow ################################################################ */

def checkForChecks(strt: Int,checkList: List[nodes.TrackingPoint],debug: Boolean,checks: List[String],comps: List[String]): (String,String) = {
	var res = ""
	var db = ""
	
	//var checks = List[String]("sizeof") 
	//var comps = List[String](">","<","==","<=",">=")
	
	
	var indexes = (strt to checkList.length-1).toList
	indexes = indexes.reverse
	
	
	if (debug){
		db += "Called at Index: "+strt+"\n"
		db += "and List: \n"

		for (ix <- indexes){
			var ele = checkList.apply(ix)
			db += ele.location.lineNumber.head+": "+getCode(ele)+", "
		}
		db += "\n"
	}
	
	var vuln = true
	
	for (ix <- indexes){ //iterate through path
	
		var ele = checkList.apply(ix)
		var cde = getCode(ele)
		
		for (chk <- checks){ //iterate trough all possiblities to check (e.g. sizeof)
		
			//SCALA HAS NO F*N BREAK OR CONTINUE	
			if (cde.contains(chk) && vuln){  //if line containt a check (e.g. size = sizeof)
			
				if (debug){	db += "CHECK: "+ele.location.lineNumber.head+": "+cde+"\n" }
				
				var idxs = indexes.slice(indexes.indexOf(ix),indexes.length-1)
				vuln = false
				
				
				for (idx <- idxs){ //check if this is also acutally used to compare (e.g. size > 1024)
				
					if (debug){ db += "--> "+getCode(checkList.apply(idx))+"\n"}
					
					var comp_ele = checkList.apply(idx)
					var comp_cde = getCode(comp_ele)
					
					for (comp <- comps){
						if (comp_cde.contains(comp)){
						
							if (debug){ db += "COMPARED: "+comp_ele.location.lineNumber.head+": "+comp_cde+"\n"}
							//ANSW: check if its right variable --> should already work!
							
							
							//OPTIONAL: check if size is actually matching!
							
							vuln = false
							
						}
					}
				} 
				
				/*
				//cde contains chk
				//ele = current line number in which check is!
				//check if this is used for buffer creation!
				//res += "HI "+ele.location.lineNumber.head+" "+cde+"\n"
				//res += "HU" +ele.id+"\n"
				//res += "FUCKU" +checkList.head
				//SCALA HAS NO F*N BREAK OR CONTINUE	
				if (vuln){
					//db += "FK THIS SHIT TOOL\n"
					try{					
						//ASSUMPTION: buffer is 1st argument to vulnerable function!
						var PLSJOERN = checkList.head.location.lineNumber.head
						var RLLY = cpg.call.lineNumber(PLSJOERN)
						for (inid <- RLLY.argument.head.asInstanceOf[Identifier].in.l){
							//IF sizeof is used to init buffer, its fine 
							//ASSUMPTION +1 is added on some point!
							//db += inid.id +";"+ele.id+"\n"
							if (inid.id.toString.equals(ele.id.toString)){
								vuln = false
								println("SET TO FALSE#2")
								//db += "REALLY?\n"								
							}/*
							else{
								res += "WTF?????\n"
							}*/
					
						}				
					} catch{
						case e: Throwable => db += "EXCEPTION DURING BUFFER INIT CHECK\n"+e
						
					}
				} */
			}
		}
			
	}
	
	if (vuln){
		println("VULNERABLE FOUND WTF ")
		res += "\n[+] Vulnerable flow found!\n"
		for (it <- indexes){
			res += checkList.apply(it).location.lineNumber.head+": "+getCode(checkList.apply(it))+"\n"
		}
		res += "\n"
	
	}
	
	return (res,db)

}


def getCode(i: nodes.TrackingPoint): String = {
	if (i.isInstanceOf[Call]){
		return i.asInstanceOf[Call].code
	}
	else if(i.isInstanceOf[MethodParameterIn]){
		return i.asInstanceOf[MethodParameterIn].code
	}
	else{
		return "Not Supported: "+i.getClass
	}
	
	
}

def checkIfVulnMethods(debug: Boolean, vulnFunc: String, cpgFile: String, types: List[String],checks: List[String],comps: List[String]) : (String,ListBuffer[(String,ListBuffer[Int])],String) = {
	var res = ""
	var db = ""
	var vulFuncs = new ListBuffer[(String,ListBuffer[Int])]();
	cpg.method
	.filter(_.callOut.name(vulnFunc))
	.l
	.foreach{ function => 
		var zw_res = "";
		var r = checkIfVuln(debug,function.name,vulnFunc,types,checks,comps)
		zw_res += r._1
		
		if (zw_res != ""){
			vulFuncs.append((function.name,r._2));
		}
		res += zw_res
		db += r._3
	}
	
	if (res != ""){
		res = "[+] Bufferoverflow found in file: "+cpgFile+"\n" +res
		
	}
	return (res,vulFuncs,db)

}

def checkIfVuln(debug: Boolean,functionName: String,vulnFunc: String, types: List[String], checks: List[String],comps: List[String]) : (String,ListBuffer[Int],String) = {
	var res = ""
	var db = ""
	if (debug){
		db += "[+] Checking function: "+functionName+"\n"
	}
	
	//val src = cpg.method.name(functionName).parameter.name("s")
	//val srcs = cpg.method.name(functionName).parameter.l.filter{ arg => types.contains(arg.typeFullName)}
	val srcs = cpg.method.name(functionName).parameter.l
	
	var lineNbrs = new ListBuffer[Int]();
	
	for (s <- srcs){

		val src = cpg.method.name(functionName).parameter.id(s.id.toString)
		val snk_candidate = cpg.method.name(functionName).callOut.name(vulnFunc)
		
		if (debug){
			db += "[+] Checking for candidates:\n"
			db += snk_candidate.reachableByFlows(src).p.toString +"\n\n"
		}
		
		
		//got candidates
		if (snk_candidate.reachableByFlows(src).l.length > 0){
			val snk = cpg.method.name(functionName).callOut
			
			if (debug){
				db += "[+] Checking for constraints...\n"
				db += snk.reachableByFlows(src).p.toString+"\n\n"	
			}
			
			
			var list = List[nodes.TrackingPoint]()		
			
			for (item <- snk.reachableByFlows(src).l){
				for (i <- item.elements){
					if (!list.contains(i)){					
						list = i :: list
					}
				}			
				
			}
			
			list = list.sortWith((x,y) => x.location.lineNumber.head < y.location.lineNumber.head)
			
			if (debug){
				for (it <- list){
					db += it.location.lineNumber.head+": "+getCode(it)+"\n"
				}
			}
			
			var checkList = list.reverse
			
			
			
			var vulnFlows = ""
			
			
			
			val flw = snk_candidate.reachableByFlows(src).l
			for (hit <- flw){
				//EDIT val lnNbr = hit.last.location.lineNumber.head
				val lnNbr = hit.elements.last.location.lineNumber.head				

				for (ix <- 0 to checkList.length -1){
					if (checkList.apply(ix).location.lineNumber.head == lnNbr){
						//vulnFlows += checkForChecks(ix,checkList,debug,checks,comps)
						var rc = checkForChecks(ix,checkList,debug,checks,comps)
						vulnFlows += rc._1
						db += rc._2
						lineNbrs.append(lnNbr)
					}					
				}
			}
			
			
			if (vulnFlows != ""){
				res += "[+] Vulnerabilites found in function: "+functionName+"\n" 
				res += vulnFlows
				res += "\n"
			}
			
		}
	}
	
	
	/*
	if (lineNbrs.length > 1){
		println("VULTEST.SC: WARNING: CURRENTLY ONLY RETURNING 1 ELEMENT AS LINE NUMBER BUT MULTIPLE FOUND!")
	}
	
	if (lineNbrs.length > 0){
		return (res,lineNbrs.head)
	} else{
		return (res, -1)
	}*/
	
	return (res,lineNbrs,db)
}


/* ########################################################   Bufferoverflow END ################################################################ */



/* ########################################################   Integer overflow ################################################################ */
def findIntegerOverflows(): (String,ListBuffer[(String,ListBuffer[Int])]) = {
	
	
	var details = ""
	var vulFuncs = new ListBuffer[(String,ListBuffer[Int])]()
	
	for (func <- cpg.method.name.l){
		var src = cpg.method.name(func).parameter
		var snk = cpg.call.name("<operator>.assignment").argument.order(1).evalType(".*short.*")
	
		var r = snk.reachableByFlows(src).p		
		if (!r.isEmpty){
			details += "Integer Overflow: \n"+r.toString+"\n\n"
			println("VULTEST.SC: TODO! FIND OUT LINENBR!!!")
			var lb = new ListBuffer[Int]()
			lb.append(-1)
			vulFuncs.append((func,lb)); //#!TODO
		}
	}
	
	if (details != ""){
		println("INTEGER OVERFLOW SEARCH:\n"+details)
		println("FOUND Vulnerable Functions:\n"+vulFuncs.toString)

	}
	
	return (details,vulFuncs)
}

/* ########################################################    Integer overflow END  ################################################################ */



/* ########################################################    MAIN  ################################################################ */

@main def main(cpgFile: String="None",outFile: String="None", summaryFile: String="None",debug: Boolean=false): Unit = {
	var total_detailed = "";
	var db = ""
	var all_vul_funcs = new ListBuffer[(String,ListBuffer[Int])]();
	
	if (cpgFile!="None"){
		loadCpg(cpgFile);
	}

	
	println("Searching for Integer Overflows...")
	var (det,vulFuncs) = findIntegerOverflows();
	total_detailed += det;
	all_vul_funcs.appendAll(vulFuncs);
	println("Searching for Integer Overflows... DONE!")
	
	
	println("Searching for Bufferoverflow...")
	
	
	//TODO: sprintf,scanf, memcpys, fread
	val vulnFunctions = List("strcpy","strcpy_trim","strcat","gets") //TODO expand
	val types = List("char *") //TODO expand currently ignored
	val checks = List("sizeof")
	val comps = List[String](">","<","==","<=",">=")
	
	vulnFunctions.foreach{
		f =>
		
		var r = checkIfVulnMethods(debug,f,cpgFile,types,checks,comps)
		total_detailed += r._1
		all_vul_funcs.appendAll(r._2)
		db += "DEBUG INFO ("+f.toString+")\n" + r._3
		db += "DEBUF INFO END\n"
	}
	
	println("Searching for Bufferoverflow... DONE!")
	
	if (db != "" && debug){
		if (outFile != None){
			val writer = new PrintWriter(new JFile(outFile+".dbg"))
			writer.write(db.toString)
			writer.close()
		}
	}

	if (total_detailed != ""){
		if (outFile != "None"){	
			val writer = new PrintWriter(new JFile(outFile));
			writer.write(total_detailed.toString());
			//writer.write(db.toString())
			writer.close();
		}
		if (summaryFile != "None"){
			val w = new FileWriter(summaryFile,true);
			for (vul <- all_vul_funcs){
				for (ln <- vul._2){
					w.write(vul._1+"; "+ln+"; "+cpg.method.name(vul._1).location.head.filename.replace("\\","/")+";\n")
				}
			}
			w.close();
		}
	}
	
	return 
}

/* ########################################################    MAIN END   ################################################################ */
