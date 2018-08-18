#include <stdio.h>
#include <string>
#include <string.h>
#include "inifile.h"

using namespace std;

#define VAR_SIZE 100
#define MAX_FILE_SIZE 1024*16

int main(int argc, char const *argv[])
{
	char filebuf[MAX_FILE_SIZE];
	memset(filebuf, 0, MAX_FILE_SIZE);
	char varbuf[VAR_SIZE];
	memset(varbuf, 0 , VAR_SIZE);

	if(argc != 5 && argc != 4) {
		printf("[read|write] filename key [ |value]\nargc=%d\n", argc);
		return -1;
	}

	string strcmd = string(argv[1]);
	string fname = string(argv[2]);
	string fkey = string(argv[3]);

	if(strcmd == "read") {
		if(1 != read_profile_string_nosection(fkey.c_str(), varbuf, VAR_SIZE, NULL, fname.c_str())) {
			printf("Read failed!\n");
			return -1;
		}
		printf("File(%s):%s=%s\n", fname.c_str(), fkey.c_str(), varbuf);
	} else if(strcmd == "write") {
		if(argc != 5) {
			printf("write filename key value\nargc=%d\n", argc);
        	return -1;
		}
		string fvalue = string(argv[4]);
		if(1 == read_profile_string_nosection(fkey.c_str(), varbuf, VAR_SIZE, NULL, fname.c_str())) {
			printf("Read File(%s):%s=%s\n", fname.c_str(), fkey.c_str(), varbuf);
        }
		if(1 != write_profile_string_nosection(fkey.c_str(), fvalue.c_str(), fname.c_str())) {
			printf("Write failed!\n");
            return -1;
		}
		printf("Write File(%s):%s=%s\n", fname.c_str(), fkey.c_str(), fvalue.c_str());
	} else {
		printf("Unknow command!\n");
		return -1;
	}
	return 0;
}
