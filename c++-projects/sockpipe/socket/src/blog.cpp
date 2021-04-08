#include<iostream>
#include <stdarg.h>

void blog(int log_level, const char* format, ...)
{
	va_list args;

	va_start(args, format);
	vprintf(format, args);
	va_end(args);
}