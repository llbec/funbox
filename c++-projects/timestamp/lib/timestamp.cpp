#include "timestamp.h"
#include <iostream>
#include <regex.h>
#include <stdlib.h>
#include <string.h>

using namespace std;

char * GettimeStr(const time_t * stamp)
{
	std::cout << "Input " << stamp << std::endl;
	return ctime(stamp);
}

bool Getstamp(const char * str, time_t & time)
{
	struct tm stm;
	int iY, iM, iD, iH, iMin, iS;

	if(!CheckTimeString(str))
	{
		return false;
	}

	memset(&stm,0,sizeof(stm));  
    iY = atoi(str);  
    iM = atoi(str+5);  
    iD = atoi(str+8);  
    iH = atoi(str+11);  
    iMin = atoi(str+14);  
    iS = atoi(str+17);

	stm.tm_year=iY-1900;
    stm.tm_mon=iM-1;  
    stm.tm_mday=iD;  
    stm.tm_hour=iH;  
    stm.tm_min=iMin;  
    stm.tm_sec=iS;

	time = mktime(&stm);

	std::cout << "Input "  << iY << "-" << iM << "-" << iD << " " << iH << ":" << iMin << ":" << iS << std::endl
			<< "Outout " << time << endl;

	return true;
}

bool CheckTimeString(const char * str)
{
	char pattern[] = "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}";
	regex_t eTime;
	int     status;
	
	if (regcomp(&eTime, pattern, REG_EXTENDED|REG_NOSUB) != 0) {
        return false;      /* Report error. */
    }
	status = regexec(&eTime, str, (size_t) 0, NULL, 0);
    regfree(&eTime);
	if(status != 0)
	{
		cout << str << " is invalid" << endl;
		return false;
	}
	return true;
}
