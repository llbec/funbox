#include "lib/sudoku_x.h"

class sudoku_9 : public Sudoku_X<3>
{
public:
    sudoku_9(){}
};

uint8 SUDOKU9[9][9] = 
{
    0, 0, 0,  0, 0, 0,  0, 0, 0,
    0, 0, 0,  0, 0, 0,  0, 0, 0,
    0, 0, 0,  0, 0, 0,  0, 0, 0,

    0, 0, 0,  0, 0, 0,  0, 0, 0,
    0, 0, 0,  0, 0, 0,  0, 0, 0,
    0, 0, 0,  0, 0, 0,  0, 0, 0,

    0, 0, 0,  0, 0, 0,  0, 0, 0,
    0, 0, 0,  0, 0, 0,  0, 0, 0,
    0, 0, 0,  0, 0, 0,  0, 0, 0
};

int main()
{
    sudoku_9 test;
    for (uint i = 0; i < 9; i++)
    {
        for(uint j = 0; j < 9; j++)
        {
            if(0 != SUDOKU9[i][j])
                test.SetUnit(i,j,SUDOKU9[i][j]);
        }
    }
	test.Show();
    return 0;
}
