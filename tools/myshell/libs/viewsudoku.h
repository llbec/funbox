#ifndef VIEWSUDOKU_H
#define VIEWSUDOKU_H
#include "sudoku_x.h"
#include "viewshell.h"

class sudoku_9 : public Sudoku_X<3>
{
public:
    sudoku_9(){}
};

class CViewSudoku : public CViewCmd
{
private:
    /*commands*/
	const std::string CMD_SETROW;
    const std::string CMD_SETCOLN;
    const std::string CMD_SETUNIT;
    const std::string CMD_SHOW;
    const std::string CMD_CALC;
    /*commands*/
    sudoku_9 sudoku9_;
    int nMaxIndex;
    int nMaxVar;
public:
    CViewSudoku();
    void SetRow(const std::vector<std::string>& vecArg);
    void SetColn(const std::vector<std::string>& vecArg);
    void SetUnit(const std::vector<std::string>& vecArg);
    void Show(const std::vector<std::string>& vecArg);
    void Calc(const std::vector<std::string>& vecArg);
    virtual void HandlerCommand(const std::vector<std::string>& vecArg);
};
#endif // VIEWSUDOKU_H