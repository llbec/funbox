#include "sudoku.h"
#include <cstring>
#include <stdio.h>
#include <iostream>
#include <time.h>

CSudoku::CSudoku(uint n) :
X_2(n),
WIDTH(n*n),
DIGIT(n*n + 1),
iresult(WIDTH*WIDTH),
form_size(sizeof(uint8)*DIGIT*WIDTH*WIDTH)
{
    MallocForm(&form);
}

CSudoku::~CSudoku()
{
    FreeForm(&form);
    for(auto var:vstages) FreeForm(&(var.form));
}

void CSudoku::MallocForm(unit_t *** ptr)
{
    (*ptr) = new unit_t * [WIDTH];
    for(uint i = 0; i < WIDTH; i++)
    {
        (*ptr)[i] = new unit_t[WIDTH];
        for(uint j = 0; j < WIDTH; j++)
        {
            (*ptr)[i][j].fix = new uint8[DIGIT];
            ClearUnit(&(*ptr)[i][j]);
        }
    }
}

void CSudoku::FreeForm(unit_t *** ptr)
{
    for(uint i = 0; i < WIDTH; i++)
    {
        for(uint j = 0; j < WIDTH; j++)
        {
            delete[] (*ptr)[i][j].fix;
            (*ptr)[i][j].fix = NULL;
        }
        delete[] (*ptr)[i];
        (*ptr)[i] = NULL;
    }
    delete[] (*ptr);
    (*ptr) = NULL;
}

void CSudoku::ClearUnit(unit_t * ptr)
{
    memset(ptr->fix, 0, DIGIT);
}

uint CSudoku::Get_X(uint x, uint y)
{
    return (x/X_2)*X_2+(y/X_2);
}

uint CSudoku::Get_Y(uint x, uint y)
{
    return (x%X_2)*X_2+(y%X_2);
}

void CSudoku::SetNull()
{
    for(uint i = 0; i < WIDTH; i++)
        for(uint j = 0; j < WIDTH; j++)
            ClearUnit(&(form[i][j]));
            
    iresult = WIDTH*WIDTH;
}

bool CSudoku::IsFinish()
{
    return (0 == iresult);
}

bool CSudoku::CheckFinish()
{
    for(uint i = 0; i < WIDTH; i++)
        for(uint j = 0; j < WIDTH; j++)
        {
            if(0 == form[i][j].fix[0])
                return false;
        }
    
    return true;
}

bool CSudoku::CheckWidth(uint val)
{
    return val < WIDTH;
}

bool CSudoku::CheckDigit(uint val)
{
    return val < DIGIT && val > 0;
}

bool CSudoku::CheckX(uint x, uint8 value, std::vector< std::pair<uint, uint> > & v_id)
{
    v_id.clear();
    if(CheckDigit(value) && CheckWidth(x)) {
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

bool CSudoku::CheckY(uint y, uint8 value, std::vector< std::pair<uint, uint> > & v_id)
{
    v_id.clear();
    if(CheckDigit(value) && CheckWidth(y)) {
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

bool CSudoku::CheckZ(uint z, uint8 value, std::vector< std::pair<uint, uint> > & v_id)
{
    v_id.clear();
    if(CheckDigit(value) && CheckWidth(z)) {
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

bool CSudoku::HandlCheckResult(std::pair< uint8, std::vector< std::pair<uint, uint> > > & pTry, const std::vector< std::pair<uint, uint> > & v_tmp, const uint8 i)
{
    if(v_tmp.size() == 1) {
        SetUnit(v_tmp[0].first, v_tmp[0].second, i);
    } else {
        if(v_tmp.size() == 0)
            return false;
        if(pTry.first == 0 || pTry.second.size() > v_tmp.size()) {
            pTry.first = i;
            pTry.second.clear();
            pTry.second.assign(v_tmp.begin(), v_tmp.end());
        }
    }
    return true;
}

bool CSudoku::Scan(std::pair< uint8, std::vector< std::pair<uint, uint> > > & pTry )
{
    std::vector< std::pair<uint, uint> > v_tmp;
    pTry.first = 0;
    pTry.second.clear();
    for(uint8 i = 1; i < DIGIT; i++)
    {
        for (uint j = 0; j < WIDTH; j++)
        {
            if(!CheckX(j, i, v_tmp)) {
                if(!HandlCheckResult(pTry, v_tmp, i))
                    return false;
            }

            if(!CheckY(j, i, v_tmp)) {
                if(!HandlCheckResult(pTry, v_tmp, i))
                    return false;
            }

            if(!CheckZ(j, i, v_tmp)) {
                if(!HandlCheckResult(pTry, v_tmp, i))
                    return false;
            }
        }
    }

    return true;
}

bool CSudoku::HanldStage()
{
    if(vstages.size() == 0)
        return false;
    
    if(vstages.back().vTry.size() > 0) {
        //memcpy(form, vstages.back().form, form_size);
        CpyForm(form, vstages.back().form);
        iresult = vstages.back().iresult;
        SetUnit(vstages.back().vTry.back().first, vstages.back().vTry.back().second, vstages.back().value);
        vstages.back().vTry.pop_back();
    } else {
        FreeForm(&(vstages.back().form));
        vstages.pop_back();
        return HanldStage();
    }
    return true;
}

bool CSudoku::IsReady()
{
    return X_2 != 0 && form != NULL;
}

void CSudoku::CpyForm(unit_t ** dest, unit_t ** src)
{
    for(int i = 0; i < WIDTH; i++)
        for(int j = 0; j < WIDTH; j++)
            for(int k = 0; k < WIDTH; k++)
                dest[i][j].fix[k] = src[i][j].fix[k];
}

void CSudoku::SetUnit(uint x, uint y, uint8 value)
{
    if(!IsReady()) {
        printf("Fatal:Init failed! reset sudoku\n");
        return;
    }
    if(!CheckWidth(x) || !CheckWidth(y) || !CheckDigit(value)) {
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

void CSudoku::Show()
{
    if(!IsReady()) {
        printf("Fatal:Init failed! reset sudoku\n");
        return;
    }
    printf("\n%d X %d sudoku:\n", WIDTH, WIDTH);
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

void CSudoku::CalcForm()
{
    if(!IsReady()) {
        printf("Fatal:Init failed! reset sudoku\n");
        return;
    }
    uint lastResult = iresult;
    uint iCount = 0;
    std::vector< std::pair<uint, uint> > vId;
    std::pair< uint8, std::vector< std::pair<uint, uint> > > pTry(0, vId);
    for(auto var:vstages) FreeForm(&(var.form));
    vstages.clear();
    printf("calc start at %d\n", (int)time(NULL));
    while(!IsFinish())
    {
        if(!Scan(pTry))
        {
            if(!HanldStage())
                break;
            continue;
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
            MallocForm(&(tStage.form));
            //memcpy(tStage.form, form, form_size);
            CpyForm(tStage.form, form);
            tStage.iresult = iresult;
            tStage.value = pTry.first;
            tStage.vTry.clear();
            tStage.vTry.assign(pTry.second.begin(), pTry.second.end());
            vstages.push_back(tStage);
            
            if(!HanldStage())
                break;
        }
    }
    printf("calc ended at %d \n", (int)time(NULL));
    Show();
}

bool CSudoku::Reset(uint n)
{
    FreeForm(&form);
    for(auto var:vstages) FreeForm(&(var.form));
    vstages.clear();
    X_2 = n;
    WIDTH = n*n;
    DIGIT = (n*n + 1);
    iresult = WIDTH*WIDTH;
    form_size = (sizeof(uint8)*DIGIT*WIDTH*WIDTH);
    MallocForm(&form);
    return IsReady();
}
