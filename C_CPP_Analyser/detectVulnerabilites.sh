BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`
tag="${BLUE}[detectVulnerabilites]${RESET} "

debug=False

binFilePath=$1
joernDir=$2
scriptPath=$3
detailedOutDir=$4
summOutPath=$5
#log="${summOutPath}detectVulnerabilities2.log"
summFile="vulFuncs.vul"

if [ ! -d $detailedOutDir ]; then
echo "${tag}Creating new output folder: ${CYAN}${detailedOutDir}${RESET}..."
mkdir $detailedOutDir
echo "${tag}Creating new output folder: ${CYAN}${detailedOutDir}${RESET}... ${GREEN}DONE!${RESET}"
fi

if [ ! -d $summOutPath ]; then
echo "${tag}Creating new output folder: ${CYAN}${summOutPath}${RESET}..."
mkdir $summOutPath
echo "${tag}Creating new output folder: ${CYAN}${summOutPath}${RESET}... ${GREEN}DONE!${RESET}"
fi 

source UPDATE

cd $binFilePath

checkVul(){
	start=$1
	end=$2
	id=$3
	pid=$BASHPID
	
	curr=0

	echo "${tag}[$start-$end] checkVul with pid $CYAN$pid($id)$RESET started!"
	for jfile in $binFilePath/*.bin.zip
	do
		skip=$((curr < $start))
		endCond=$((curr >= $end))
		
		curr=$(( $curr+1 ))
		
		
		if [[ $skip -eq 1 ]]; then
			continue
		fi
		
		if [[ $endCond -eq 1 ]]; then
			echo "End condition reached."
			return
		fi

		fileName=($(echo $jfile | tr "/" "\n"))
		fileName=${fileName[-1]}
		fileName=${fileName/\.bin\.zip/""}	

		#content=$(cat $log)

		#if [[ $content == *"$fileName"* ]]; then
			#echo "${tag}Skipping, already processed"
		#	continue
			#file already processed, e.g. resuming
		#fi


		#echo "${tag}Testing ${CYAN}${fileName}${RESET}..."

#		(cd $joernDir &&
#			./joern --script "${scriptPath}vulTest.sc" --params "cpgFile=${binFilePath}${fileName}.bin.zip,\
#outFile=${detailedOutDir}jQ_${fileName}.txt,\
#summaryFile=${summOutPath}${summFile}") >/dev/null 2>&1 || echo "ERROR" > ${detailedOutDir}er_$fileName # >/dev/null 2>&1)

		(cd $joernDir &&
				./joern --script "${scriptPath}vulTest.sc" --params "cpgFile=${binFilePath}${fileName}.bin.zip,\
outFile=${detailedOutDir}jQ_${fileName}.txt,\
summaryFile=${summOutPath}${summFile},debug=${debug}") 2>${detailedOutDir}er_$fileName 1>/dev/null	
		
		if [[ $(cat ${detailedOutDir}er_$fileName) == "" ]]; then
			rm ${detailedOutDir}er_$fileName		
		fi

		updateCur $pid $id
		#echo "${tag}[${curr}/${end}(${total})]Testing ${CYAN}${fileName}${RESET}... ${GREEN}DONE!${RESET}"

	done
	
	echo "${tag}[$start-$end] checkVul with pid $CYAN$pid($id)$RESET $GREEN DONE! $RESET"
	doneId $id $pid
}



total=$(ls *.bin.zip | wc -l)
batches=1
maxP=20
currP=0
id=0

multi=$((total > 500))

if [[ $multi -eq 1 ]]; then
	batches=$((total / 500))
	batches=$((batches + 1))
fi


echo "${tag} Got a total of ${CYAN}$total files${RESET}!"


for batch in $(seq $batches)
do
	start=$(((batch-1) * 500))
	end=$((batch * 500))
	
	if [[ $currP -eq $maxP ]]; then
		echo "Waiting since max processes reached."
		wait -n
		currP=$((currP - 1))
	fi
	
	checkVul $start $end $id &
	
	id=$((id + 1))
	currP=$((currP + 1))
	
done

wait

#remove duplicates

cp "${summOutPath}${summFile}" "${summOutPath}${summFile}_orig"
sort -u "${summOutPath}${summFile}_orig" > "${summOutPath}${summFile}"

echo "${tag}All files processed!"


