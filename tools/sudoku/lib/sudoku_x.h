#ifndef SUDOKU_X_H
#define SUDOKU_X_H

//#include <vector>
#include <cstring>
#include <stdio.h>
#include <iostream>

typedef unsigned char  uint8;
typedef unsigned int   uint;

template<uint XVAL>
class Sudoku_X
{
protected:
    enum { X_2=XVAL, WIDTH=XVAL*XVAL, DIGIT };
    struct unit_t{
        char fix[DIGIT];

        void SetNull()
        {
            memset(fix, 0, sizeof(fix));
        }
    };
    unit_t form[WIDTH][WIDTH];
    unit_t * grid[WIDTH][WIDTH];
    uint iresult = WIDTH * WIDTH;
public:
    Sudoku_X()
    {
        for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
            {
                form[i][j].SetNull();
                grid[(i/X_2)*X_2+(j/X_2)][(i%X_2)*X_2+(j%X_2)] = &form[i][j];
            }
    }
    void SetNull()
    {
        for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
                form[i][j].SetNull();
    }
    bool IsFinish(){ return (0 == iresult); };
    bool CheckFinish()
    {
        for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
            {
                if(0 == form[i][j].fix)
                    return false;
            }
        
        return true;
    }
    bool CheckWidth(uint val) { return val < WIDTH; };
    bool CheckDigit(uint val) { return val < DIGIT; };
    void Show()
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
    void SetUnit(uint x, uint y, uint8 value)
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
};

#endif
