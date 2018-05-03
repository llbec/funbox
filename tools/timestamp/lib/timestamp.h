#ifndef TIMESTAMP_H
#define TIMESTAMP_H

#include <stdio.h>
#include <time.h>
#include <string>

//void HelloFunc();
char * GettimeStr(const time_t * stamp);
bool Getstamp(const char * str, time_t & time);
bool CheckTimeString(const char * str);
#endif
