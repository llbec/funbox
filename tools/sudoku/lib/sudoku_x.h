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
    Sudoku_X();
    void SetNull();
    bool IsFinish(){ return (0 == iresult); };
    bool CheckFinish();
    bool CheckWidth(uint val) { return val < WIDTH };
    bool CheckDigit(uint val) { return val < DIGIT };
    void Show();
    void SetUnit(uint x, uint y, uint8 value);
};

#endif
