#ifndef VIEW_SHELL_H
#define VIEW_SHELL_H
#include <stdio.h>
#include <string>
#include <vector>
#include <map>

//typedef void (*FP_CMD)(const std::vector<std::string>& vecArg);

class CViewCmd
{
public:
    const std::string _name;
private:
    std::map <std::string, CViewCmd*> mapViews_;
    std::map <std::string, int> mapCommand_;
    bool IsVaildCmd(std::string str);
public:
    enum GetWordRet {
        get_no,
        get_one,
        get_multi,
        get_match
    };
    CViewCmd(std::string name);
    void Handler(std::vector<std::string>& vecCmd, std::vector<CViewCmd *>& vecRetView);
    void GetPossible(std::vector<std::string>& vecRet, std::string str);
    int GetWord(std::vector<char>& vecRet, std::string str);
    bool LogonView(CViewCmd* pView);
    virtual void HandlerCommand(const std::vector<std::string>& vecArg){}
};

class CViewBase
{
private:
    CViewCmd tBaseView_;
    std::vector<CViewCmd *> stackViews_;
public:
    CViewBase();
    CViewCmd* CurrentView();
    void GetKeyList(std::string str, std::vector<std::string>& vecList);
    std::string GetKeyEnd(std::string str);
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