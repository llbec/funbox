#ifndef SUDOKU_X_H
#define SUDOKU_X_H

typedef unsigned char  uint8;
typedef unsigned int   uint;

typedef struct unit_t{
    uint8 fix;
    std::vector<uint8> may;
    std::vector<uint8> need;
    std::vector<uint8> cannot;
};

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