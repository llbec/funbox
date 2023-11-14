#include <stdio.h>
#include <stdlib.h>

void i2array(int src, unsigned char * array)
{
	*array = src >> 24;
	*(array + 1) = src >> 16;
	*(array + 2) = src >> 8;
	*(array + 3) = src;
}

void i2array(int src, unsigned char * array, int idx)
{
	array[idx] = src >> 24;
	array[idx + 1] = src >> 16;
	array[idx + 2] = src >> 8;
	array[idx + 3] = src;	
}

int array2i(unsigned char * array)
{
	int a = 0;
	a |= *array << 24;
	a |= *(array + 1) << 16;
	a |= *(array + 2) << 8;
	a |= *(array + 3);
	return a;	
}

int array2i(unsigned char * array, int idx)
{
	int a = 0;
	a |= array[idx] << 24;
	a |= array[idx + 1] << 16;
	a |= array[idx + 2] << 8;
	a |= array[idx + 3];
	return a;
}

void testInt(int a)
{
	unsigned char buffer[4];
	i2array(a, buffer, 0);
	printf("%d:\t\t[%3u,%3u,%3u,%3u]\t%d\n", a, buffer[0], buffer[1], buffer[2], buffer[3], array2i(buffer, 0));
}

float Bytes2Float(unsigned char index, unsigned char * array)
{
    float fVar;
    void * pf;
    unsigned char i;
    pf = &fVar;
    for (i = 0; i < 4; i++)
    {
        *((unsigned char*)pf + i) = array[index + i];
    }
    return fVar;
}

void Float2Bytes(float fVar, unsigned char index, unsigned char * array)
{
    void * pf;
    unsigned char i;

    pf = &fVar;
    for (i = 0; i < 4; i++)
    {
        array[index + i] = *((unsigned char*)pf + i);
    }
}

void testFloat(float fVar)
{
	unsigned char buffer[4];
	Float2Bytes(fVar, 0, buffer);
	printf("%f:\t\t[%3u,%3u,%3u,%3u]\t%f\n", fVar, buffer[0], buffer[1], buffer[2], buffer[3], Bytes2Float(0, buffer));
}

int main()
{
	int a;
	float f;
	
	for (int i = 0; i < 10; i++)
	{
		a = rand();
		testInt(a);
		testInt(~(a-1));
		testFloat((float)rand() / (float)a);
	}
	return 0;
}
