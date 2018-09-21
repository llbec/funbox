#include "viewshell.h"

/*
 * __GNUC        => linux
 * __MSC_VER    => window
 */
#ifdef __GNUC__
#ifdef __APPLE__
#include <termios.h>
#else
#include <termio.h>
#endif // __APPLE__
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
        if(GetString().empty()) {
            bTab_ = true;
            return true;
        }
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
    if(vecLine_.empty()) return;
    vecLine_.pop_back();
    bTab_ = false;
    printf("\b \b");
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
    printf("%s>", sTitle_.c_str());
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

void CViewBase::GetKeyList(std::string str, std::vector<std::string>& vecList)
{
    string schar = "";
    for(unsigned int i = 0; i < str.length(); i++)
    {
        char c = *(str.begin() + i);
        if(c != ' ') {
            schar += c;
        } else {
            vecList.push_back(schar);
            schar = "";
        }
    }
    vecList.push_back(schar);
}

std::string CViewBase::GetKeyEnd(std::string str)
{
    string schar = "";
    if(str.length() < 1) return schar;
    if(*(str.end() - 1) == ' ') return " ";
    for(unsigned int i = 1; i <= str.length(); i++)
    {
        char c = *(str.end() - i);
        if(c != ' ') {
            schar.insert(0, 1, c);
        } else {
            break;
        }
    }
    return schar;
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
            vector<CViewCmd*> vecView;
            vector<string> vecCmd;
            GetKeyList(str, vecCmd);
            CurrentView()->Handler(vecCmd, vecView);
            for(auto var : vecView) stackViews_.push_back(var);
            sRet = CurrentView()->_name;
        } catch (int exp) {
            exp == -1 ? printf("FATAL: Stack of command view is empty!\n") : printf("FATAL: Command quit passed!\n");
            return false;
        }
    }
    return true;
}

bool CViewBase::GetPossible(std::vector<std::string>& vecRet, std::string str)
{
    try {
        vector<string> vecCmd;
        GetKeyList(str, vecCmd);
        CurrentView()->GetPossible(vecRet, vecCmd);
    } catch (int exp) {
        exp == -1 ? printf("FATAL: Stack of command view is empty!\n") : printf("FATAL:view map is NULL\n");
        return false;
    }
    return true;
}
int CViewBase::GetWord(std::vector<char>& vecRet, std::string str)
{
    try {
        vector<string> vecCmd;
        GetKeyList(str, vecCmd);
        return CurrentView()->GetWord(vecRet, vecCmd);
    } catch (int exp) {
        exp == -1 ? printf("FATAL: Stack of command view is empty!\n")  : printf("FATAL:view map is NULL\n");
        return -1;
    }
}

CViewCmd::CViewCmd(std::string name) :
_name(name)
{}

void CViewCmd::GetPossible(std::vector<std::string>& vecRet, std::vector<std::string>& vecArgs)
{
    vecRet.clear();
    if(vecArgs.empty()) {
        for(auto var : mapViews_) vecRet.push_back(var.first);
		for (auto var : mapCommand_) vecRet.push_back(var.first);
    } else {
        string str = vecArgs[0];
        for(auto var : mapViews_)
        {
            string::size_type idx = var.first.find(str);
            if(0 == idx) vecRet.push_back(var.first);
        }
        if(vecRet.size() == 1) {
            if(vecRet[0] == str && vecArgs.size() > 1) {
                vecArgs.erase(vecArgs.begin());
                CViewCmd* ptrtemp = GetNextView(str);
                if(ptrtemp == NULL) throw -2;
                vecRet.clear();
                ptrtemp->GetPossible(vecRet, vecArgs);
                return;
            }
        }
        string sCmd = "";
        for(auto var : mapCommand_)
        {
            string::size_type idx = var.first.find(str);
            if(0 == idx) {
                vecRet.push_back(var.first);
                sCmd = var.first;
            }
        }
        if(!sCmd.empty() && vecRet.size() == 1) {
            vecRet.clear();
            HelpCommand(vecRet, sCmd);
            return;
        }
    }
}

int CViewCmd::GetWord(std::vector<char>& vecRet, std::vector<std::string>& vecArgs)
{
    if(vecArgs.empty()) return get_no;
    string str = vecArgs[0];
    vecRet.clear();
    vector<string> vecMatchs;
    string::size_type idx = string::npos;
    for(auto varView : mapViews_)
    {
        idx = varView.first.find(str);
        if(0 == idx) vecMatchs.push_back(varView.first);
        idx = string::npos;
    }
    if(vecMatchs.size() == 1) {
        if(vecMatchs[0] == str && vecArgs.size() > 1) {
            vecArgs.erase(vecArgs.begin());
            CViewCmd* ptrtemp = GetNextView(str);
            if(ptrtemp == NULL) throw -2;
            return ptrtemp->GetWord(vecRet, vecArgs);
        }
    }
    for(auto varCmd : mapCommand_)
    {
        idx = varCmd.first.find(str);
        if(0 == idx) vecMatchs.push_back(varCmd.first);
        idx = string::npos;
    }
    if(vecMatchs.size() == 1) {
        if(vecMatchs[0] == str) {
            return get_match;
        }
        //idx = vecMatchs[0].find(str);
        vecRet.assign(vecMatchs[0].begin() + str.length(), vecMatchs[0].end());
        return get_one;
    } else if (vecMatchs.size() > 1) {
        return get_multi;
    }
    return get_no;
}

void CViewCmd::Handler(std::vector<std::string>& vecCmd, std::vector<CViewCmd *>& vecRetView)
{
    if(vecCmd.size() == 0) return;
    vector<std::string>::iterator it = vecCmd.begin();
    if(mapCommand_.count(*it) != 0) {
        HandlerCommand(vecCmd);
        vecRetView.clear();
        return;
    }
    if(mapViews_.count(*it) != 0) {
        string str = *it;
        vecCmd.erase(it);
        vecRetView.push_back(mapViews_[str]);
        mapViews_[str]->Handler(vecCmd, vecRetView);
    }
    return;
}

bool CViewCmd::IsVaildCmd(std::string str)
{
    if(str.empty()) return false;
    /*more rules*/
    return true;
}

bool CViewCmd::LogonView(CViewCmd* pView)
{
    if(pView == NULL) return false;
    if(!IsVaildCmd(pView->_name)) return false;
    if(mapViews_.count(pView->_name) != 0) {
        if(mapViews_[pView->_name] != pView)
            return false;
        return true;
    }
    mapViews_.insert(make_pair(pView->_name, pView));
    return true;
}

bool CViewCmd::LogonCmd(std::string str)
{
    if(str.empty()) return false;
    if(mapCommand_.count(str) != 0) return false;
    mapCommand_.insert(make_pair(str, 1));
    return true;
}

CViewCmd* CViewCmd::GetNextView(std::string name)
{
    return mapViews_[name];
}
