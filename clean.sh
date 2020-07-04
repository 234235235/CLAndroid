#main stuff
mainPath=$1 

#Database
neo4jBin=$2 
db_Uri=$3
db_User=$4
db_Pword=$5
windows=$6

BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

clean(){
	delete="MATCH (n) DETACH DELETE n;"
	echo "Cleaning DB..."
	./cypher-shell -u $db_User -p $db_Pword "${delete}"
	echo "Cleaning DB... ${GREEN}DONE!${RESET}"
}


clean_db(){
	status=$(./neo4j status)
	if [[ $status = *"not"* ]]; then
		./neo4j start
		sleep 5
		clean
		./neo4j stop
	else
		clean
	fi
}




tag="${RED}[Clean] ${RESET}"
(cd $neo4jBin && clean_db)
