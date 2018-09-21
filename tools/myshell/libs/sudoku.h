#ifndef SUDOKU_H
#define SUDOKU_H
#include <vector>

typedef unsigned char  uint8;
typedef unsigned int   uint;

class CSudoku
{
private:
    uint X_2;
    uint WIDTH; //X_2 * X_2
    uint DIGIT; //WIDTH + 1
    struct unit_t{
        uint8* fix;
    };
    unit_t** form;
    uint iresult;
    uint form_size;

    struct stage_t{
        unit_t** form;
        uint iresult;
        uint8 value;
        std::vector< std::pair<uint, uint> > vTry;
    };
    std::vector<stage_t> vstages;

    void MallocForm(unit_t *** ptr);
    void FreeForm(unit_t *** ptr);
    void ClearUnit(unit_t * ptr);
    uint Get_X(uint x, uint y);
    uint Get_Y(uint x, uint y);
    void SetNull();
    bool IsFinish();
    bool CheckFinish();
    bool CheckWidth(uint val);
    bool CheckDigit(uint val);
    bool CheckX(uint x, uint8 value, std::vector< std::pair<uint, uint> > & v_id);
    bool CheckY(uint y, uint8 value, std::vector< std::pair<uint, uint> > & v_id);
    bool CheckZ(uint z, uint8 value, std::vector< std::pair<uint, uint> > & v_id);
    bool HandlCheckResult(std::pair< uint8, std::vector< std::pair<uint, uint> > > & pTry, const std::vector< std::pair<uint, uint> > & v_tmp, const uint8 i);
    bool Scan(std::pair< uint8, std::vector< std::pair<uint, uint> > > & pTry );
    bool HanldStage();
    bool IsReady();

public:
    CSudoku(uint n = 3);
    ~CSudoku();
    void SetUnit(uint x, uint y, uint8 value);
    void Show();
    void CalcForm();
    bool Reset(uint n);
};
#endif // SUDOKU_H