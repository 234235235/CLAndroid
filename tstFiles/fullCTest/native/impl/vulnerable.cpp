void callMe(char* s){
    doinNothing(s);
}

void doinNothing(char* s){
    vulnerable(s);
}

void vulnerable(char* s) {
	char buf[1024];
	int size = sizeof(s);

	strcpy(buf, s);
}