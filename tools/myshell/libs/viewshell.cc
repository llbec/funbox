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

using namespace std;

CViewShell::CViewShell(CViewBase * ptr)
{
    pObj_ = ptr;
    sTitle_ = pObj_->CurrentView()->_name;
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
    string sLine;
    sLine.insert(sLine.begin(), vecLine_.begin(), vecLine_.end());
    return sLine;
}

void CViewShell::PutChar(char c)
{
    vecLine_.push_back(c);
    printf("%c", c);
}

void CViewShell::PutString(std::string str)
{
    vecLine_.insert(vecLine_.end(), str.begin(), str.end());
    printf("%s", str.c_str());
}

void CViewShell::PutNewLine(std::string str = "")
{
    printf("\n%s>", sTitle_.c_str());
    Clear();
    if(str != "") PutString(str);
}

bool CViewShell::HandlerTab()
{
    if(bTab_) {
        vector<string> vecOpt;
        if(!pObj_->GetPossible(vecOpt, GetString())) return false;
        printf("\n");
        for(auto var : vecOpt)
            printf("%s\t", var.c_str());
        PutNewLine(GetString());
    } else {
        vector<char> vecWord;
        int iret = pObj_->GetWord(vecWord, GetString());
        switch(iret)
        {
            case CViewCmd::get_one:
                for(auto var : vecWord)
                    PutChar(var);
                bTab_ = false;
                break;
            case CViewCmd::get_match:
                PutChar(' ');
                bTab_ = false;
                break;
            case CViewCmd::get_no:
                bTab_ = false;
                break;
            case CViewCmd::get_multi:
                bTab_ = true;
                break;
            default:
                return false;
        }
    }
    return true;
}

void CViewShell::HandlerBackspace()
{
    vecLine_.pop_back();
    bTab_ = false;
    printf("\b \b%c",'\0');
}

bool CViewShell::HandlerEnter()
{
    if(!pObj_->Handler(GetString(), sTitle_)) {
        printf("\n");
        return false;
    }
    PutNewLine();
    return true;
}

void CViewShell::HandlerChar()
{
    PutChar(cGet_);
    bTab_ = false;
}

void CViewShell::Run()
{
    while(true){
        cGet_ = sh_getch();
        if(cGet_ == '\0')
            continue;
        else if(cGet_ == '\t') {
            if(!HandlerTab()) break;
        } else if(cGet_ == '\b') {
            HandlerBackspace();
        } else if(cGet_ == '\r') {
            if(!HandlerEnter()) break;
        } else {
            HandlerChar();
        }
        cGet_ = '\0';
    }
}

CViewBase::CViewBase() : 
tBaseView_("base")
{
    stackViews_.push_back(&tBaseView_);
}

CViewCmd* CViewBase::CurrentView()
{
    if(stackViews_.size() <= 0)
        throw -1;
    return stackViews_[stackViews_.size() - 1];
}

bool CViewBase::Handler(std::string str, std::string& sRet)
{
    if(str == "quit") {
        if(stackViews_.size() == 1)
            return false;
        else {
            stackViews_.pop_back();
            sRet = CurrentView()->_name;
        }
        return true;
    } else {
        try {
            //what's value for sRet
            vector<CViewCmd*> vecView;
            return CurrentView()->Handler(vecView, str);
        } catch (int exp) {
            exp == -1 ? printf("FATAL: Stack of command view is empty!\n") : printf("FATAL: Command quit passed!\n");
            return false;
        }
    }
}
bool CViewBase::GetPossible(std::vector<std::string>& vecRet, std::string str)
{
    try {
        CurrentView()->GetPossible(vecRet, str);
    } catch (int exp) {
        printf("FATAL: Stack of command view is empty!\n");
        return false;
    }
    return true;
}
int CViewBase::GetWord(std::vector<char>& vecRet, std::string str)
{
    try {
        return CurrentView()->GetWord(vecRet, str);
    } catch (int exp) {
        printf("FATAL: Stack of command view is empty!\n");
        return -1;
    }
}

CViewCmd::CViewCmd(std::string name) :
_name(name)
{}

void CViewCmd::GetPossible(std::vector<std::string>& vecRet, std::string str)
{
    vecRet.clear();
    if(str == _name) {
        for(auto var : mapViews_)
            vecRet.push_back(var.first);
    } else {
        for(auto var : mapViews_)
        {
            string::size_type idx = var.first.find(str);
            if(0 == idx) vecRet.push_back(var.first);
        }
    }
}

int CViewCmd::GetWord(std::vector<char>& vecRet, std::string str)
{
    vecRet.clear();
    vector<string> vecMatchs;
    string::size_type idx = string::npos;
    for(auto var : mapViews_)
    {
        idx = var.first.find(str);
        if(0 == idx) vecMatchs.push_back(var.first);
        idx = string::npos;
    }
    if(vecMatchs.size() == 1) {
        if(vecMatchs[0] == str) {
            return get_match;
        }
        idx = vecMatchs[0].find(str);
        vecRet.assign(vecMatchs[0].begin() + str.length(), vecMatchs[0].end());
        return get_one;
    } else {
        if (vecMatchs.size() == 0)
            return get_no;
        return get_multi;
    }
}

bool CViewCmd::Handler(std::vector<CViewCmd*>& vecRet, std::string str)
{
    if(str == "quit")
        throw 0;
    return true;
}
