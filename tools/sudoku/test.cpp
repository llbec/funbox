#include "lib/sudoku_x.h"
#include <stdlib.h>
#include <string.h>

class sudoku_9 : public Sudoku_X<3>
{
public:
    sudoku_9(){}
};

uint8 SUDOKU9[9][9] = 
{
    {0, 0, 0,  0, 0, 0,  8, 0, 0},
    {0, 0, 0,  0, 0, 0,  0, 0, 0},
    {0, 0, 0,  0, 0, 0,  0, 0, 0},

    {0, 0, 0,  0, 0, 0,  0, 0, 0},
    {0, 0, 0,  0, 0, 0,  0, 0, 0},
    {0, 0, 0,  0, 0, 0,  0, 0, 0},

    {0, 0, 0,  0, 0, 0,  0, 0, 0},
    {0, 0, 0,  0, 0, 0,  0, 0, 0},
    {0, 0, 0,  0, 0, 0,  0, 0, 0}
};

int main(int argc, char* argv[])
{
    if(argc!=1) // help 
    {
       printf("./test_sudoku filepath\n");
       return 1;
    }
    sudoku_9 test;

    /*read file*/
    FILE * ptrData = fopen(std::string(argv[0]).c_str(), "r");
    if(ptrData == NULL){ printf("Error: could't open file data.ini\n"); return 2;}
    // obtain file size:
    fseek(ptrData, 0, SEEK_END);
    uint iSize = (uint)ftell (ptrData);
    rewind (ptrData);

    char * buffer= (char*) malloc (sizeof(char)*iSize);
    if (buffer == NULL) { printf("Error: Memory error\n"); return 3;}

    // copy the file into the buffer:
    uint result = fread (buffer,1,iSize,ptrData);
    //if (result != iSize) { printf("Error: Reading error\n"); return 4;}

    char * pSplit = ",{}\n "; 
    char * p = strtok(buffer, pSplit);
	int index = 0;
    while(p != NULL)
    {
    	if(index >= 9*9)
   		{
		   	printf("out range\n");
		   	return 0;
	   	}
    	SUDOKU9[index/9][index%9] = (uint8)atoi(p);
    	index++;
    	p = strtok(NULL, pSplit);
    }

    for (uint i = 0; i < 9; i++)
    {
        for(uint j = 0; j < 9; j++)
        {
            if(0 != SUDOKU9[i][j])
                test.SetUnit(i,j,SUDOKU9[i][j]);
            
            printf("%3d", SUDOKU9[i][j]);
	    	if(j % 3 == 2)
	    		printf("   ");
        }
        printf("\n");
	    if(i % 3 == 2)
   			printf("\n\n");
    }
    
	test.Show();

    test.CalcForm();
    return 0;
}
