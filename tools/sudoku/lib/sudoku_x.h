#ifndef SUDOKU_X_H
#define SUDOKU_X_H

#include <vector>
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

        void SetNull(){ memset(fix, 0, sizeof(fix)); }
        uint MemSize(){ return sizeof(uint8)*DIGIT;}
    };
    unit_t form[WIDTH][WIDTH];
    uint iresult;
    const uint form_size;

    struct stage_t{
        unit_t form[WIDTH][WIDTH];
        uint iresult;
        uint8 value;
        std::vector< std::pair<uint, uint> > vTry;
    };

    std::vector<stage_t> vstages;
public:
    Sudoku_X():form_size(sizeof(uint8)*DIGIT*WIDTH*WIDTH)
    {
        for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
                form[i][j].SetNull();

        iresult = WIDTH*WIDTH;
    }
    uint Get_X(uint x, uint y){ return (x/X_2)*X_2+(y/X_2); }
    uint Get_Y(uint x, uint y){ return (x%X_2)*X_2+(y%X_2); }
    void SetNull()
    {
        for(uint i = 0; i < WIDTH; i++)
            for(uint j = 0; j < WIDTH; j++)
                form[i][j].SetNull();
                
        iresult = WIDTH*WIDTH;
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
        if(!CheckWidth(x) || !CheckWidth(y) || !CheckDigit(value))
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
            
            uint z = Get_X(x,y);
            if(i != Get_Y(x, y))
                form[Get_X(z,i)][Get_Y(z,i)].fix[value] = 1;
        }
    }

    bool CheckX(uint x, uint8 value, std::vector< std::pair<uint, uint> > & v_id)
    {
        v_id.clear();
        if(CheckDigit(value) && CheckWidth(x))
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                if(form[x][j].fix[0] == value)
                    return true;
                if(form[x][j].fix[value] == 0)
                    v_id.push_back(std::make_pair(x,j));
            }
        }
        return false;
    }

    bool CheckY(uint y, uint8 value, std::vector< std::pair<uint, uint> > & v_id)
    {
        v_id.clear();
        if(CheckDigit(value) && CheckWidth(y))
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                if(form[j][y].fix[0] == value)
                    return true;
                if(form[j][y].fix[value] == 0)
                    v_id.push_back(std::make_pair(j,y));
            }
        }
        return false;
    }

    bool CheckZ(uint z, uint8 value, std::vector< std::pair<uint, uint> > & v_id)
    {
        v_id.clear();
        if(CheckDigit(value) && CheckWidth(z))
        {
            for(uint j = 0; j < WIDTH; j++)
            {
                if(form[Get_X(z,j)][Get_Y(z,j)].fix[0] == value)
                    return true;
                if(form[Get_X(z,j)][Get_Y(z,j)].fix[value] == 0)
                    v_id.push_back(std::make_pair(Get_X(z,j),Get_Y(z,j)));
            }
        }
        return false;
    }

    bool HandlCheckResult(std::pair< uint8, std::vector< std::pair<uint, uint> > > & pTry, const std::vector< std::pair<uint, uint> > & v_tmp, const uint8 i)
    {
        if(v_tmp.size() == 1)
        {
            SetUnit(v_tmp[0].first, v_tmp[0].second, i);
        }
        else
        {
            if(v_tmp.size() == 0)
                return false;
            if(pTry.first == 0 || pTry.second.size() > v_tmp.size())
            {
                pTry.first = i;
                pTry.second.clear();
                pTry.second.assign(v_tmp.begin(), v_tmp.end());
            }
        }
        return true;
    }

    bool Scan(std::pair< uint8, std::vector< std::pair<uint, uint> > > & pTry )
    {
        std::vector< std::pair<uint, uint> > v_tmp;
        for(uint8 i = 1; i < DIGIT; i++)
        {
            for (uint j = 0; j < WIDTH; j++)
            {
                if(!CheckX(j, i, v_tmp))
                {
                    if(!HandlCheckResult(pTry, v_tmp, i))
                        return false;
                }

                if(!CheckY(j, i, v_tmp))
                {
                    if(!HandlCheckResult(pTry, v_tmp, i))
                        return false;
                }

                if(!CheckZ(j, i, v_tmp))
                {
                    if(!HandlCheckResult(pTry, v_tmp, i))
                        return false;
                }
            }
        }

        return true;
    }

    bool HanldStage()
    {
        if(vstages.size() == 0)
            return false;
        
         if(vstages.back().vTry.size() > 0)
         {
            memcpy(form, vstages.back().form, form_size);
            iresult = vstages.back().iresult;
            SetUnit(vstages.back().vTry.back().first, vstages.back().vTry.back().second, vstages.back().value);
            vstages.back().vTry.pop_back();
         }
         else
         {
            vstages.pop_back();
            return HanldStage();
         }
         return true;
    }

    void CalcForm()
    {
        uint lastResult = iresult;
        uint iCount = 0;
		std::vector< std::pair<uint, uint> > vId;
        std::pair< uint8, std::vector< std::pair<uint, uint> > > pTry(0, vId);
        printf("calc start at %d\n", (int)time(NULL));
        while(!IsFinish())
        {
            if(!Scan(pTry))
            {
                if(!HanldStage())
                    break;
            }
            if(lastResult == iresult)
                iCount ++;
            else
            {
                iCount = 0;
                lastResult = iresult;
            }
            if(iCount > 3)
            {
                stage_t tStage;
                memcpy(tStage.form, form, form_size);
                tStage.iresult = iresult;
                tStage.value = pTry.first;
                tStage.vTry.clear();
                tStage.vTry.assign(pTry.second.begin(), pTry.second.end());
                vstages.push_back(tStage);
                if(!HanldStage())
                    break;
            }
        }
        printf("calc ended at %d\n", (int)time(NULL));

        Show();
    }
};

#endif
