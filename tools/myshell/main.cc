#include "viewshell.h"
#include "viewsudoku.h"

int main(int argc, char* argv[])
{
    CViewBase tCmdMan;
    CViewSudoku tSudoku();
    tCmdMan.CurrentView()->LogonView((CViewCmd *)&tSudoku);
    CViewShell myShell(&tCmdMan);
    myShell.Run();
    return 0;
}