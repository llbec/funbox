#ifndef SUDOKU_X_H
#define SUDOKU_X_H

//#include <vector>
#include <cstring>
#include <stdio.h>
#include <iostream>
#include <time.h>

typedef unsigned char  uint8;
typedef unsigned int   uint;

template<uint XVAL>
class Sudoku_X
{
protected:
    enum { X_2=XVAL, WIDTH=XVAL*XVAL, DIGIT };
    struct unit_t{
        uint8 fix[DIGIT];

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
    uint Get_X(uint x, uint y){ return (x/X_2)*X_2+(y/X_2); }
    uint Get_Y(uint x, uint y){ return (x%X_2)*X_2+(y%X_2); }
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
                if(0 == form[i][j].fix[0])
                    return false;
            }
        
        return true;
    }
    bool CheckWidth(uint val) { return val < WIDTH; };
    bool CheckDigit(uint val) { return val < DIGIT && val > 0; };
    void Show()
    {
        std::cout << X_2 << " X " << X_2 << " sudoku:" << std::endl;
        for(uint i = 0; i < WIDTH; i++)
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                printf("%3d ", (int)form[i][j].fix[0]);
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
        if(!CheckWidth(x) || !CheckWidth(y) || CheckDigit(value))
        {
            printf("Invaild width x = %d or y = %d or value = %d\n", x, y, value);
            return;
        }
        form[x][y].fix[0] = value;
        for(uint i = 1; i < DIGIT; i++)
        {
            if(i == value)
                form[x][y].fix[i] = 0;
            else
                form[x][y].fix[i] = 1;
        }
        iresult--;
        for (uint i = 0; i < WIDTH; i++)
        {
            if(i != x)
                form[i][y].fix[value] = 1;
            
            if(i != y)
                form[x][i].fix[value] = 1;
            
            if(i != Get_Y(x, y))
                grid[Get_X(x,y), i]->fix[value] = 1;
        }
    }

    bool CheckX(uint x, uint8 value, uint8 & sum, uint & position)
    {
        sum = 0;
        position = DIGIT;
        if(CheckDigit(value) && CheckWidth(x))
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                sum += form[x][j].fix[value];
                if(form[x][j].fix[0] == value)
                    return true;
                if(form[x][j].fix[value] == 0)
                    position = j;
            }
        }
        return false;
    }

    bool CheckY(uint y, uint8 value, uint8 & sum, uint & position)
    {
        sum = 0;
        position = DIGIT;
        if(CheckDigit(value) && CheckWidth(y))
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                sum += form[j][y].fix[value];
                if((uint8)form[j][y].fix[0] == value)
                    return true;
                if(form[j][y].fix[value] == 0)
                    position = j;
            }
        }
        return false;
    }

    bool CheckZ(uint z, uint8 value, uint8 & sum, uint & position)
    {
        sum = 0;
        position = DIGIT;
        if(CheckDigit(value) && CheckWidth(z))
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                sum += grid[z][j]->fix[value];
                if((uint8)grid[z][j]->fix[0] == value)
                    return true;
                if(form[z][j]->fix[value] == 0)
                    position = j;
            }
        }
        return false;
    }

    void Scan()
    {
        uint8 sum = 0;
        uint position = DIGIT;
        for(uint8 i = 1; i < DIGIT; i++)
        {
            for (uint j = 0; j < WIDTH; j++)
            {
                if(!CheckX(j, i, sum, position))
                {
                    if(WIDTH - 1 == sum)
                    {
                        SetUnit(j, position, i);
                    }
                }

                if(!CheckY(j, i, sum, position))
                {
                    if(WIDTH - 1 == sum)
                    {
                        SetUnit(position, j, i);
                    }
                }

                if(!CheckZ(j, i, sum, position))
                {
                    if(WIDTH - 1 == sum)
                    {
                        SetUnit(Get_X(j, position), Get_Y(j, position), i);
                    }
                }
            }
        }
    }

    void CalcForm()
    {
        printf("calc start at %d\n", (int)time(NULL));
        while(!IsFinish())
        {
            Scan();
        }
        printf("calc ended at %d\n", (int)time(NULL));

        Show();
    }
};

#endif
