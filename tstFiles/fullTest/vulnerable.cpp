#include <cstring>


int vulnerable(char* s) {
	char buf[1024];
	int size = sizeof(s);

	strcpy(buf, s);
	
	return -200;
}

int doinNothing(char* s){
    return vulnerable(s);
}


int callMe(char* s){
    return doinNothing(s);
}