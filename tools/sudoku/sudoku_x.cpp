#include "sudoku_x.h"

template<uint MAX>
base_form<MAX>::base_form()
{
        memset(data, 0, sizeof(data));
}