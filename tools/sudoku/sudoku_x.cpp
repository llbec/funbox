#include "sudoku_x.h"

template<uint MAX>
base_form<MAX>::base_form()
{
    for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
                form[i][j].SetNull();
}
