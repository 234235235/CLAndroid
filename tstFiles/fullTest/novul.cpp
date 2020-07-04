#include <cstring>


int vulnerable(char* s) {
	int size = sizeof(s);
	char buf[size+1];
	strcpy(buf, s);
	
	return -200;
}

int doinNothing(char* s){
    return vulnerable(s);
}


int callMe(char* s){
    return doinNothing(s);
}