#ifndef SUDOKU_X_H
#define SUDOKU_X_H

//#include <vector>
#include <cstring>
#include <stdio.h>
#include <iostream>

typedef unsigned char  uint8;
typedef unsigned int   uint;

/*struct unit_t{
    uint8 fix;
    //std::vector<uint8> may;
    std::vector<uint8> need;
    std::vector<uint8> cannot;

    void SetNull()
    {
        fix = 0;
        //may.clear();
        need.clear();
        cannot.clear();
    }
};*/

template<uint XVAL>
class Sudoku_X
{
protected:
    enum { X_2=XVAL, WIDTH=XVAL*XVAL };
    struct unit_t{
        uint8 fix;
        //std::vector<uint8> may;
        //std::vector<uint8> need;
        //std::vector<uint8> cannot;
		uint need[WIDTH];
        uint cannot[WIDTH];

        void SetNull()
        {
            fix = 0;
            //may.clear();
            //need.clear();
            //cannot.clear();
			memset(need, 0, sizeof(need));
            memset(cannot, 0, sizeof(cannot));
        }
    };
    unit_t form[WIDTH][WIDTH];
    unit_t * grid[WIDTH][WIDTH];
    uint iresult = WIDTH * WIDTH;
public:
    
};

#endif
