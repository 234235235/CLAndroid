#!/bin/bash
BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${BLUE}[grep_loads]${RESET} "
done="${GREEN}DONE!${RESET}"
skip="${tag}${RED}SKIPPED!${RESET}"


grep_path="S:\Uni\Master\MasterArbeit\frameworks\base\\"
out_path="S:\Uni\Master\MasterArbeit\Analysis\JNI_LIB_Finder\Output\JNIs\\"

loads=("System.load(" "System.loadLibrary(" "Runtime.load(" "Runtime.loadLibrary(")


for l in ${loads[@]}; do
	echo "${tag} Grepping for ${CYAN}${l}${RESET}..."
	(cd $grep_path &&
		grep ${l} -r > ${out_path}${l}.txt )
	echo "${tag} Results written to ${out_path}" 
	echo "${tag} Grepping for ${CYAN}${l}${RESET}... ${done}"
done

