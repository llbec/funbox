#include "sudoku_x.h"

template <uint XVAL>
Sudoku_X<XVAL>::Sudoku_X()
    {
        for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
            {
                form[i][j].SetNull();
                grid[(i/X_2)*X_2+(j/X_2)][(i%X_2)*X_2+(j%X_2)] = &form[i][j];
            }
    }

template <uint XVAL>
void Sudoku_X<XVAL>::SetNull()
{
    for(uint i = 0; i < WIDTH; i++)
        for(uint j = 0; j < WIDTH; j++)
            form[i][j].SetNull();
}

template <uint XVAL>
bool Sudoku_X<XVAL>::CheckFinish()
{
    for(uint i = 0; i < WIDTH; i++)
        for(uint j = 0; j < WIDTH; j++)
        {
            if(0 == form[i][j].fix)
                return false;
        }
    
    return true;
}

template <uint XVAL>
void Sudoku_X<XVAL>::Show()
{
    std::cout << X_2 << " X " << X_2 << " sudoku:" << std::endl;
    for(uint i = 0; i < WIDTH; i++)
    {
        for(uint j = 0; j < WIDTH; j++)
        {
            printf("%3d ", form[i][j].fix);
            if((j+1)%X_2 == 0)
                printf("  ");
        }
        printf("\n");
        if((i+1)%X_2 == 0)
            printf("\n");
    }
}

template <uint XVAL>
void Sudoku_X<XVAL>::SetUnit(uint x, uint y, uint8 value)
{
    if(!CheckWidth(x) || !CheckWidth(y))
    {
        printf("Invaild width x = %d or y = %d\n", x, y);
        return;
    }
    form[x][y].fix[0] = value;
    for(uint i = 1; i < DIGIT; i++)
    {
        if(i == value)
            form[x][y].fix[i] = 1;
        else
            form[x][y].fix[i] = -1;
    }
}


// Explicit instantiations for Sudoku_X<3>
template Sudoku_X<3>::Sudoku_X();
template void Sudoku_X<3>::SetNull();
template bool Sudoku_X<3>::CheckFinish();
template void Sudoku_X<3>::Show();
template void Sudoku_X<3>::SetUnit(uint x, uint y, uint8 value);