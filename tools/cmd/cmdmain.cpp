#include "readchar.h"
#include "cmdhandler.h"

int main(int argc, char* argv[])
{
    CCmdHandler tCmd;
    CReadChar<CCmdHandler> tRead(&tCmd);
    tRead.Run();
    return 0;
}