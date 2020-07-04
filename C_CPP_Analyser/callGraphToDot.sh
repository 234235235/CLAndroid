BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${BLUE}[callGraphToDot]${RESET} "

joernDir=$1
binFilePath=$2 
outDir=$3 
scriptDir=$4
inclOut=$5
modus=$6		


if [ ! -d $outDir ]; then
echo "${tag}Creating new output folder: ${CYAN}${outDir}${RESET}..."
mkdir $outDir
echo "${tag}Creating new output folder: ${CYAN}${outDir}${RESET}... ${GREEN}DONE!${RESET}"
fi

if [ ! -d $inclOut ]; then
echo "${tag}Creating new output folder: ${CYAN}${inclOut}${RESET}..."
mkdir $inclOut
echo "${tag}Creating new output folder: ${CYAN}${inclOut}${RESET}... ${GREEN}DONE!${RESET}"
fi 

tmp_process=p2
alive_check=ac
hangT=50

rm $alive_check

updateCur(){

	echo 1 >> $tmp_process
	pt=0
	while read line;
	do
		pt=$(( pt + 1))
	done < $tmp_process
	
	
	curT=$(date +%s)

	if [[ -f $alive_check ]]; then
		sed -i "/${1}(${2})/d" ./$alive_check
	fi

	echo "${1}(${2});$curT" >> $alive_check	
	
	chk=$((pt%50))
		
	if [[ $chk -eq 0 ]]; then
		while read line;
		do
			
			pidd=($(echo $line | tr ";" "\n"))
			last=${pidd[-1]}
			pidd=${pidd[0]}

			
			diff=$((curT - $last))
			
			if [[ $diff -gt $hangT ]]; then
				echo "$RED${pidd} Hang (since $diff seconds)!$RESET"
			fi
		
		done < $alive_check
	fi

	

	print=$(( pt % 20 ))

	if [[ $print == 0 ]]; then
		echo "${tag}[${1}(${2})] Proccessed: ${pt}/${total}"
	fi
}

createCG(){
	start=$1
	end=$2
	
	curr=0
	dir="NONE"
	ending="NONE"	


	if [[ $modus == *"FAST"* ]]; then
		dir=$inclOut
		ending="*.incl"
	else
		dir=$binFilePath
		ending="*bin.zip"
	fi


	pid=$BASHPID
	id=$3

	echo "${tag}[$start-$end]createCG with pid $CYAN$pid($id)$RESET started!"

	for jOut in $dir$ending
	do	

		skip=$((curr < $start))
		endCond=$((curr >= $end))

		curr=$((curr + 1))

		if [[ $skip -eq 1 ]]; then
			continue
		fi

		if [[ $endCond -eq 1 ]]; then
			echo "${tag}End condition reached."
			break
		fi
		
		
		name=($(echo $jOut | tr "/" "\n"))
		name=${name[-1]}
		
		if [[ $modus == *"FAST"* ]]; then
			name=${name/\.incl/""}
		
		else
			name=${name/\.bin\.zip/""}
		fi

		#echo "${tag}Processing ${CYAN}${jOut}${RESET} ..."
		updateCur $pid $id

		if [[ -f "${outDir}${name}.dot" ]]; then
			#echo "${tag}Skipping since cg already exists."
			#curr=$((curr+1))
			continue
		fi
	
		
		(cd $joernDir &&
			./joern --script "${scriptDir}callGraphToDot.sc" --params "cpgFile=${binFilePath}${name}.bin.zip,outFile=${outDir}${name}.dot" >/dev/null 2>&1)  #,inclOut=${inclOut}${name}.incl") # >/dev/null 2>&1)
	


		#curr=$((curr+1))	
	
		#echo "${tag}[${curr}/${total}]Processing ${CYAN}${jOut}${RESET} ... ${GREEN}DONE!${RESET}"
	done 

	echo "${tag}[$start-$end]createCG with pid $CYAN${pid}(${id})$RESET $GREEN DONE! $RESET."

	sed -i "/${pid}(${id})/d" ./$alive_check

}



total=0

if [[ $modus == *"FAST"* ]]; then
	total=$(find $inclOut -maxdepth 1 -type f -name "*.incl" | wc -l)
else
	total=$(find $binFilePath -maxdepth 1 -type f -name "*.bin.zip" | wc -l)
fi

multi=$(( total > 100 ))
batches=1
rm $tmp_process
split=50

if [[ $multi -eq 1 ]]; then
	batches=$((total / $split))
	batches=$((batches + 1))
fi

echo "${tag}Got a total of ${CYAN}$total files${RESET}!"

maxthreads=20
cur_threads=0
id=0
for batch in $(seq $batches)
do
	
	start=$(((batch-1) * $split))
	end=$((batch * $split))
	
	if [[ $cur_threads -eq $maxthreads ]]; then
		echo "Waiting cuz maxthreads reached"
		wait -n 
		cur_threads=$((cur_threads - 1 ))
	fi
	
	createCG $start $end $id &
	cur_threads=$(( cur_threads + 1))
	id=$((id + 1))

done

wait

echo "${tag}All files processed!"


