#include "viewshell.h"

/*
 * __GNUC        => linux
 * __MSC_VER    => window
 */
#ifdef __GNUC__

#include <termio.h>
/*
 * get one char from  input
 * return: int
 */
int sh_getch(void) {
    int cr;
    struct termios nts, ots;

    if (tcgetattr(0, &ots) < 0) // 得到当前终端(0表示标准输入)的设置
        return EOF;

    nts = ots;
    cfmakeraw(&nts); // 设置终端为Raw原始模式，该模式下所有的输入数据以字节为单位被处理
    if (tcsetattr(0, TCSANOW, &nts) < 0) // 设置上更改之后的设置
        return EOF;

    cr = getchar();
    if (tcsetattr(0, TCSANOW, &ots) < 0) // 设置还原成老的模式
        return EOF;

    return cr;
}

#elif _MSC_VER

#include <conio.h>
#define sh_getch    _getch

#else
    #error "error : Currently only supports the Visual Studio and GCC!"
#endif

CViewShell::CViewShell(CViewCmd * ptr)
{
    pObj_ = ptr;
    Clear();
}

void CViewShell::Clear()
{
    bTab_ = false;
    cGet_ = '\0';
    vecLine_.clear();
}

std::string CViewShell::GetString()
{
    std::string sLine;
    sLine.insert(sLine.begin(), vecLine_.begin(), vecLine_.end());
    return sLine;
}

void CViewShell::HandlerTab()
{
    if(bTab_) {
        std::vector<std::string> vecOpt;
        pObj_->GetPossible(vecOpt, GetString());
        printf("\n");
        for(auto var : vecOpt)
            printf("%s\t", var.c_str());
        printf("\n%s", GetString().c_str());
    } else {
        std::vector<char> vecWord;
        pObj_->GetWord(vecWord, GetString());
        for(auto var : vecWord)
        {
            vecLine_.push_back(var);
            printf("%c", var);
        }
        bTab_ = false;
    }
}

void CViewShell::HandlerBackspace()
{
    vecLine_.pop_back();
    bTab_ = false;
    printf("\b \b%c",'\0');
}

bool CViewShell::HandlerEnter()
{
    if(!pObj_->Handler(GetString())) {
	printf("\n");
        return false;
    }
    printf("\n");
    Clear();
    return true;
}

void CViewShell::HandlerChar()
{
    vecLine_.push_back(cGet_);
    bTab_ = false;
    printf("%c", cGet_);
}

void CViewShell::Run()
{
    while(true){
        cGet_ = sh_getch();
        if(cGet_ == '\0')
            continue;
        else if(cGet_ == '\t')
            HandlerTab();
        else if(cGet_ == '\b')
            HandlerBackspace();
        else if(cGet_ == '\r') {
            if(!HandlerEnter())
                break;
        } else
            HandlerChar();
        cGet_ = '\0';
    }
}

bool CViewCmd::Handler(std::string str)
{
    if(str == "quit")
        return false;
    return true;
}
