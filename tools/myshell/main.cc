#include "viewshell.h"

int main(int argc, char* argv[])
{
    CViewBase tCmd;
    CViewShell myShell(&tCmd);
    myShell.Run();
    return 0;
}