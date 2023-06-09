#include <stdio.h>

#define VARIABLE 3

float arr[VARIABLE][VARIABLE] = { {2,1,-1}, {-3,-1,2}, {-2,1,2} };
float result[VARIABLE] = {8,-11,-3};

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
	for(i = 0; i < VARIABLE; i++)
	{
		if(arr[x][i] != 0 && x != i) return -1;
	}
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

int main()
{
	int i,j;
	if (Gauss() < 0) printf("ERROR\n");
	for(i = 0; i < VARIABLE; i++)
	{
		for(j = 0; j < VARIABLE; j++) printf("%f \t", arr[i][j]);
		printf("\t***\t %f \n", result[i]);
	}
}
