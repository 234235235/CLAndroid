BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${BLUE}[transferToDatabase]${RESET} "

scriptPath=$1
localCallGraphsDotFormat=$2
includes=$3
db_Uri=$4
db_User=$5
db_Pword=$6
crossCalls=$7
directory=$8
py=$9
errFile=${10}
srcFilePath=${11}
time_log=${12}


if [ ! -d $crossCalls ]; then
echo "${tag}Creating new output folder: ${CYAN}${crossCalls}${RESET}..."
mkdir $crossCalls
echo "${tag}Creating new output folder: ${CYAN}${crossCalls}${RESET}... ${GREEN}DONE!${RESET}"
fi

touch $errFile

echo "${tag}Creating neo4j callgraph... "
echo "${tag}Using python version: $($py --version)"



toneo(){
	start=$1
	end=$2
	total=$3
	id=$4
	pid=$BASHPID

	echo "${tag}[$start-$end]createGlobalCG with pid $CYAN$pid($id)$RESET started!"
	(cd $scriptPath && $py createGlobalCallGraph.py $localCallGraphsDotFormat $db_Uri $db_User $db_Pword $crossCalls $directory LOAD $start $end $total)

	
	echo "${tag}[$start-$end]createGlobalCG with pid $CYAN$pid($id)$RESET $GREEN DONE! $RESET"
}






total=$(ls $localCallGraphsDotFormat | wc -l)
split=20
batches=$((total/ $split))
batches=$((batches +1 ))

maxthreads=20
cur_threads=0
id=0

source "${directory}GETDIFF"

strt=$(date)
for batch in $(seq $batches)
do
	start=$(((batch-1) * $split))
	end=$((batch * $split))

	if [[ $cur_threads -eq $maxthreads ]]; then
		echo "Waiting cuz maxthreads reached"
		wait -n
		cur_threads=$((cur_threads - 1))
	fi

	toneo $start $end $total $id &
	id=$((id + 1))
	cur_threads=$(( cur_threads + 1))
done

wait

stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::transferToDatabase:::Load $res" >> $time_log
echo "$tag All files loaded!"

echo "$tag Linking..."
strt=$(date)

(cd $scriptPath && $py createGlobalCallGraph.py $localCallGraphsDotFormat $db_Uri $db_User $db_Pword $crossCalls $directory "LOADED.FULL")

stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::transferToDatabase:::Link $res" >> $time_log
echo "$tag Linking $GREEN DONE! $RESET"


echo "${tag}Creating neo4j callgraph... ${GREEN}DONE!${RESET}"
