#include <stdio.h>

typedef unsigned char BYTE;

int main()
{
	BYTE buff[2] = {0x09,0xE3};
	BYTE PREF[2] = {1,3};
	BYTE VAL[2] = {0,0};
	float temp, v_tref, t_ref = 25, K = 0.2262, c_tref = 2292;
	int comp2;
	temp = (buff[0] << 8) + buff[1];
	v_tref = PREF[0] == 0 ? c_tref + PREF[1] : c_tref - PREF[1];
	v_tref = v_tref * 2500 / 4096;
	temp = (temp * 2500 / 4096 - v_tref) * K + t_ref;
	printf("temperature is %f\n", temp);
	
	comp2 = temp * 256;
	VAL[0] = comp2 >= 0 ? ((comp2 & 0x7FFF) >> 8) : (((comp2 & 0x7FFF) >> 8) | 0x80);
	VAL[1] = comp2;
	printf("2Complement is [%2X, %2X]\n", VAL[0], VAL[1]);
	return 0;
}