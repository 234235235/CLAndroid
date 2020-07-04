BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${BLUE}[JAVA_MAIN] ${RESET}"
done="${GREEN}DONE!${RESET}"

vulSummaryResolvedCsv=$1 
test_path=$2
java_out=$3 
totalSummary=$4
c_cpp_analyser_scripts=$5/scripts
db_Uri=$6
db_User=$7
db_Pword=$8
directory=$9
py=${10}
time_log=${11}

source "${directory}GETDIFF"

if [[ ! -d $java_out ]]; then
	mkdir $java_out
fi


echo "${tag}Linking java src files to compiled jars..."
strt=$(date)
$py matchJavaSrcToJar.py $vulSummaryResolvedCsv $test_path $java_out |& tee "${java_out}J_matchJavaSrcToJar.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "Java_Analyser:::matchJavaSrcToJar $res" >> $time_log
echo "${tag}Linking java src files to compiled jars... ${done}"
#exit 0

echo "${tag}Tracing back calls in Java code..."
strt=$(date)
./backTrack.sh $java_out $totalSummary |& tee "${java_out}J_backTrack.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "Java_Analyser:::backTrack $res" >> $time_log
echo "${tag}Tracing back calls in Java code... ${done}"
#exit 0

echo "${tag}Resolving local Java CGS (jni Bridges)..."
strt=$(date)
$py resolve_jar_to_src_callgraph.py $java_out |& tee "${java_out}J_resolve_jar_to_src_callgraph.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "Java_Analyser:::resolveJarToSrc $res" >> $time_log
echo "${tag}Resolving local Java CGS (jni Bridges)... ${done}"
#exit 0


if [ ! -d "$java_out/LocalBackTrackCGs" ]; then
	echo "${tag}${RED}No Local Backtrack Cgs created${RESET} (At least not to: ${CYAN}${java_out}/LocalBackTrackCGs${RESET})!"
	echo "${tag}${RED}Skipping Loading java CGs and linking them to global CG!${RESET}"
	exit 0
fi	       

       
echo "${tag}Loading CGs into global graph..."
strt=$(date)
(cd $c_cpp_analyser_scripts &&
    $py createGlobalCallGraph.py $java_out/LocalBackTrackCGs $db_Uri $db_User $db_Pword "" $directory "LOAD") |& tee "${java_out}J_load_global_graph.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "Java_Analyser:::Load $res" >> $time_log
echo "${tag}Loading CGs into global graph... ${done}"
#exit 0

echo "${tag}Linking together JNI CALLs..."
strt=$(date)
$py linkJNIGlobalCG.py $java_out/summary.csv $db_Uri $db_User $db_Pword $directory |& tee "${java_out}J_linkJNIGlobalCG.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "Java_Analyser:::Link $res" >> $time_log
echo "${tag}Linking together JNI CALLs... ${done}"
#exit 0
