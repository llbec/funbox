#include "viewsudoku.h"

using namespace std;

CViewSudoku::CViewSudoku() : 
CViewCmd("sudoku"),
CMD_SETROW("row"),
CMD_SETCOLN("column"),
CMD_SETUNIT("unit"),
CMD_SHOW("show"),
CMD_CALC("calc"),
nMaxIndex(8),
nMaxVar(9)
{
    LogonCmd(CMD_SETROW);
    LogonCmd(CMD_SETCOLN);
    LogonCmd(CMD_SETUNIT);
    LogonCmd(CMD_SHOW);
    LogonCmd(CMD_CALC);
}

void CViewSudoku::SetRow(const std::vector<std::string>& vecArg)
{
    if(vecArg.size() < 2 || vecArg.size() > 11) {
        printf("\nHelp:row Index value1 ...\nExample:row 3 0 1 2 3 4 5 6 7 8");
        return;
    }
    if(vecArg[0] != CMD_SETROW) return;
    int nRow = atoi(vecArg[1].c_str());
    if(nRow < 0 || nRow > nMaxIndex) {
        printf("\nInvalid row index. [0,%d]", nMaxIndex);
        return;
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        int n = atoi(vecArg[i].c_str());
        if(n < 1 || n > nMaxVar) {
            printf("\nInvalid value. [1,%d]", nMaxVar);
            return;
        }
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        sudoku9_.SetUnit(nRow, (i - 2), atoi(vecArg[i].c_str()));
    }
}

void CViewSudoku::SetColn(const std::vector<std::string>& vecArg)
{
    if(vecArg.size() < 2 || vecArg.size() > 11) {
        printf("\nHelp:column Index value1 ...\nExample:column 3 0 1 2 3 4 5 6 7 8");
        return;
    }
    if(vecArg[0] != CMD_SETCOLN) return;
    int nColn = atoi(vecArg[1].c_str());
    if(nColn < 0 || nColn > nMaxIndex) {
        printf("\nInvalid column index. [0,%d]", nMaxIndex);
        return;
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        int n = atoi(vecArg[i].c_str());
        if(n < 1 || n > nMaxVar) {
            printf("\nInvalid value. [1,%d]", nMaxVar);
            return;
        }
    }
    for(unsigned int i = 2; i < vecArg.size(); i++)
    {
        sudoku9_.SetUnit((i - 2), nColn, atoi(vecArg[i].c_str()));
    }
}

void CViewSudoku::SetUnit(const std::vector<std::string>& vecArg)
{
    if(vecArg.size() != 4) {
        printf("\nHelp:unit x y value\nExample:unit 3 4 1");
        return;
    }
    if(vecArg[0] != CMD_SETUNIT) return;
    int x = atoi(vecArg[1].c_str());
    if(x < 0 || x > nMaxIndex) {
        printf("\nInvalid row index. [0,%d]", nMaxIndex);
        return;
    }
    int y = atoi(vecArg[2].c_str());
    if(y < 0 || y > nMaxIndex) {
        printf("\nInvalid column index. [0,%d]", nMaxIndex);
        return;
    }
    int var = atoi(vecArg[3].c_str());
    if(var < 1 || var > nMaxVar) {
        printf("\nInvalid value. [1,%d]", nMaxVar);
        return;
    }
    sudoku9_.SetUnit(x, y, var);
}

void CViewSudoku::Show(const std::vector<std::string>& vecArg)
{
    sudoku9_.Show();
}

void CViewSudoku::Calc(const std::vector<std::string>& vecArg)
{
    sudoku9_.CalcForm();
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
}
