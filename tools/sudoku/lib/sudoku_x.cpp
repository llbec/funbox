#include "sudoku_x.h"

template <uint XVAL>
void Sudoku_X<XVAL>::SetNull()
{
    for(uint i = 0; i < WIDTH; i++)
        for(uint j = 0; j < WIDTH; j++)
            form[i][j].SetNull();
}

