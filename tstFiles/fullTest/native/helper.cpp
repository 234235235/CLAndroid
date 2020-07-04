#include "header/vulnerable.hpp"

int safe (char* s){
	return callMe(s);
}