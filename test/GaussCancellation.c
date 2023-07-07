#include <stdio.h>
#include <math.h>

#define VARIABLE 6

float arr[VARIABLE][VARIABLE];// = { {2,1,-1}, {-3,-1,2}, {-2,1,2} };
float result[VARIABLE];// = {8,-11,-3};

int CancellationDown(int x, int y)
{
	int i;
	float coefficient;
	if(x <= y || x < 1) return -1;
	coefficient = arr[x][y] / arr[y][y];
	for(i = y; i < VARIABLE; i++)
	{
		arr[x][i] = arr[x][i] - arr[y][i] * coefficient;	
	}
	result[x] = result[x] - result[y] * coefficient;
	return 0;
}

int CancellationUp(int x, int y)
{
	int i;
	float coefficient;
	if(x >= y || x > VARIABLE - 2) return -1;
	coefficient = arr[x][y] / arr[y][y];
	for(i = y; i > x; i--)
	{
		arr[x][i] = arr[x][i] - arr[y][i] * coefficient;
	}
	result[x] = result[x] - result[y] * coefficient;
	return 0;
}

int ToOne(int x)
{
	int i;
	if (arr[x][x] == 0) return result[x] == 0 ? 0 :-1;
	/*for(i = 0; i < VARIABLE; i++)
	{
		if(arr[x][i] != 0 && x != i) return -1;
	}*/
	result[x] = result[x] / arr[x][x];
	arr[x][x] = 1;
	return 0;
}

int Gauss()
{
	int x,y;
	for(y = 0; y < VARIABLE-1; y++)
	{
		for(x = y+1; x < VARIABLE; x++)
		{
			if (CancellationDown(x, y) < 0) return -1;
		}
	}
	for(y = VARIABLE - 1; y > 0; y--)
	{
		for(x = y-1; x >= 0; x--)
		{
			if (CancellationUp(x, y) < 0) return -1;
		}
	}
	for(x = 0; x < VARIABLE; x++)
	{
		if (ToOne(x) < 0) return -1;
	}
	return 0;
}

float calc(float x)
{
	float y = 0;
	int i;
	for(i = 0; i < VARIABLE; i++)
	{
		y += result[i] * pow(x, 5-i);
	}
	return y;
}

int main()
{
	int i,j;
	
	float adc[VARIABLE] = {0x8E0,0x3C0,0x1BD,0xD3,0x6D,0x31};
	float rep[VARIABLE] = {400, 200, 100, 50, 25, 12.5};
	
	for(i = 0; i < VARIABLE; i++)
	{
		for(j = 0; j < VARIABLE; j++)
		{
			arr[i][j] = pow(adc[i], 5-j);
		}
		result[i] = rep[i];
	}
	
	if (Gauss() < 0) printf("ERROR\n");
	for(i = 0; i < VARIABLE; i++)
	{
		for(j = 0; j < VARIABLE; j++) printf("%f \t", arr[i][j]);
		printf("\t*** %f \n\n", result[i]);
	}
	
	printf("__________________\n");
	
	for(i = 0; i < VARIABLE; i++)
	{
		printf("%f = %f\n", adc[i], calc(adc[i]));
	}
}
