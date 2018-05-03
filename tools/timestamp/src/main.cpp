#include "timestamp.h"
#include <string>
#include <iostream>

using namespace std;

int main()
{
	string strInput = "start";
	cout << strInput << ": input 'quit' to quit" << endl;
	time_t stamp;

	while(strInput != "quit")
	{
		getline(cin,strInput);
		Getstamp(strInput.c_str(), stamp);
	}
	return 0;
}
