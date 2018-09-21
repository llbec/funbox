#include "viewsudoku.h"

using namespace std;

CViewSudoku::CViewSudoku() : 
CViewCmd("sudoku"),
CMD_SETROW("row"),
CMD_SETCOLN("column"),
CMD_SETUNIT("unit"),
CMD_SHOW("show"),
CMD_CALC("calc"),
CMD_SETSIZE("setsize"),
nBase_(3),
nMaxIndex_(8),
nMaxVar_(9)
{
    pSudoku_ = new CSudoku((unsigned int)nBase_);
    LogonCmd(CMD_SETROW);
    LogonCmd(CMD_SETCOLN);
    LogonCmd(CMD_SETUNIT);
    LogonCmd(CMD_SHOW);
    LogonCmd(CMD_CALC);
    LogonCmd(CMD_SETSIZE);
}

void CViewSudoku::SetRow(const std::vector<std::string>& vecArg)
{
    if(pSudoku_ == NULL) {
        printf("\nFatal:memory error,reset sudoku");
        return;
    }
    if(vecArg.size() < 2 || vecArg.size() > 11) {
        printf("\nHelp:row Index value1 ...\nExample:row 3 0 1 2 3 4 5 6 7 8");
        return;
    }
    if(vecArg[0] != CMD_SETROW) return;
    int nRow = atoi(vecArg[1].c_str());
    if(nRow < 0 || nRow > nMaxIndex_) {
        printf("\nInvalid row index. [0,%d]", nMaxIndex_);
        return;
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        int n = atoi(vecArg[i].c_str());
        if(n < 1 || n > nMaxVar_) {
            printf("\nInvalid value. [1,%d]", nMaxVar_);
            return;
        }
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        pSudoku_->SetUnit(nRow, (i - 2), atoi(vecArg[i].c_str()));
    }
}

void CViewSudoku::SetColn(const std::vector<std::string>& vecArg)
{
    if(pSudoku_ == NULL) {
        printf("\nFatal:memory error,reset sudoku");
        return;
    }
    if(vecArg.size() < 2 || vecArg.size() > 11) {
        printf("\nHelp:column Index value1 ...\nExample:column 3 0 1 2 3 4 5 6 7 8");
        return;
    }
    if(vecArg[0] != CMD_SETCOLN) return;
    int nColn = atoi(vecArg[1].c_str());
    if(nColn < 0 || nColn > nMaxIndex_) {
        printf("\nInvalid column index. [0,%d]", nMaxIndex_);
        return;
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        int n = atoi(vecArg[i].c_str());
        if(n < 1 || n > nMaxVar_) {
            printf("\nInvalid value. [1,%d]", nMaxVar_);
            return;
        }
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        pSudoku_->SetUnit((i - 2), nColn, atoi(vecArg[i].c_str()));
    }
}

void CViewSudoku::SetUnit(const std::vector<std::string>& vecArg)
{
    if(pSudoku_ == NULL) {
        printf("\nFatal:memory error,reset sudoku");
        return;
    }
    if(vecArg.size() != 4) {
        printf("\nHelp:unit x y value\nExample:unit 3 4 1");
        return;
    }
    if(vecArg[0] != CMD_SETUNIT) return;
    int x = atoi(vecArg[1].c_str());
    if(x < 0 || x > nMaxIndex_) {
        printf("\nInvalid row index. [0,%d]", nMaxIndex_);
        return;
    }
    int y = atoi(vecArg[2].c_str());
    if(y < 0 || y > nMaxIndex_) {
        printf("\nInvalid column index. [0,%d]", nMaxIndex_);
        return;
    }
    int var = atoi(vecArg[3].c_str());
    if(var < 1 || var > nMaxVar_) {
        printf("\nInvalid value. [1,%d]", nMaxVar_);
        return;
    }
    pSudoku_->SetUnit(x, y, var);
}

void CViewSudoku::Show(const std::vector<std::string>& vecArg)
{
    if(pSudoku_ == NULL) {
        printf("\nFatal:memory error,reset sudoku");
        return;
    }
    pSudoku_->Show();
}

void CViewSudoku::Calc(const std::vector<std::string>& vecArg)
{
    if(pSudoku_ == NULL) {
        printf("\nFatal:memory error,reset sudoku");
        return;
    }
    pSudoku_->CalcForm();
}

void CViewSudoku::SetSize(const std::vector<std::string>& vecArg)
{
    if(vecArg.size() != 2) {
        printf("\nHelp:setsize size(Sudoku's width is size*size)\nExample:setsize 4(Means sudoku 16x16)");
        return;
    }
    delete pSudoku_;
    pSudoku_ = NULL;
    int nSize = atoi(vecArg[1].c_str());
    if(nSize < 1) {
        printf("\nInvalid size!");
        return;
    }
    nBase_ = nSize;
    nMaxIndex_ = (nBase_*nBase_) - 1;
    nMaxVar_ = nBase_*nBase_;
    pSudoku_ = new CSudoku((unsigned int) nBase_);
    pSudoku_ == NULL ? printf("\nReset size failed, try again!") : printf("\nNew sudoku %d x %d",nMaxVar_, nMaxVar_);
}

void CViewSudoku::HandlerCommand(const std::vector<std::string>& vecArg)
{
    if(vecArg.empty()) return;
    string scmd = vecArg[0];
    if(scmd == CMD_SETROW) SetRow(vecArg);
    else if(scmd == CMD_SETCOLN) SetColn(vecArg);
    else if(scmd == CMD_SETUNIT) SetUnit(vecArg);
    else if(scmd == CMD_SHOW) Show(vecArg);
    else if(scmd == CMD_CALC) Calc(vecArg);
    else if(scmd == CMD_SETSIZE) SetSize(vecArg);
}
