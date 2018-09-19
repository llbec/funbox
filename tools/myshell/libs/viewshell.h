#ifndef VIEW_SHELL_H
#define VIEW_SHELL_H
#include <stdio.h>
#include <string>
#include <vector>
#include <map>


class CViewCmd
{
public:
    const std::string _name;
    typedef void (*FP_CMD)(int, char const **);
private:
    std::map <std::string, CViewCmd*> mapViews_;
    std::map <std::string, FP_CMD> mapCommand_;
public:
    enum GetWordRet {
        get_no,
        get_one,
        get_multi,
        get_match
    };
    CViewCmd(std::string name);
    bool Handler(std::vector<CViewCmd*>& vecRet, std::string str);
    void GetPossible(std::vector<std::string>& vecRet, std::string str);
    int GetWord(std::vector<char>& vecRet, std::string str);
};

class CViewBase
{
private:
    CViewCmd tBaseView_;
    std::vector<CViewCmd *> stackViews_;
public:
    CViewBase();
    CViewCmd* CurrentView();
    bool Handler(std::string str, std::string& sRet);
    bool GetPossible(std::vector<std::string>& vecRet, std::string str);
    int GetWord(std::vector<char>& vecRet, std::string str);
};

class CViewShell
{
private:
    bool bTab_;
    char cGet_;
    std::vector<char> vecLine_;
    CViewBase * pObj_;
    std::string sTitle_;
public:
    CViewShell(CViewBase * ptr);
    void Clear();
    std::string GetString();
    bool HandlerTab();
    void HandlerBackspace();
    bool HandlerEnter();
    void HandlerChar();
    void Run();
    void PutChar(char c);
    void PutString(std::string str);
    void PutNewLine(std::string str);
};
#endif // VIEW_SHELL_H