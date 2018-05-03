#ifndef SUDOKU_X_H
#define SUDOKU_X_H

typedef unsigned char  uint8;
typedef unsigned int   uint;

template<uint MAX>
class base_form
{
protected:
    enum { WIDTH=MAX };
    uint8 data[WIDTH][WIDTH];
public:
    base_form()
    {
        memset(data, 0, sizeof(data));
    }
};

#endif