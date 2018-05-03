#include "sudoku_x.h"

template<uint XVAL>
void base_form<XVAL>::SetNull()
{
    for(uint i = 0; i < WIDTH; i++)
        for(uint j = 0; j < WIDTH; j++)
            form[i][j].SetNull();
}

