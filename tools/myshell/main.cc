#include "viewshell.h"

int main(int argc, char* argv[])
{
    CViewCmd tCmd;
    CViewShell myShell(&tCmd);
    myShell.Run();
    return 0;
}