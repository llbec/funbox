#ifndef VIEW_SHELL_H
#define VIEW_SHELL_H
#include <stdio.h>
#include <string>
#include <vector>

class CViewCmd
{
public:
    CViewCmd(){}
    bool Handler(std::string str);
    void GetPossible(std::vector<std::string>& vecRet, std::string str) {}
    void GetWord(std::vector<char>& vecRet, std::string str) {}
};

class CViewShell
{
private:
    bool bTab_;
    char cGet_;
    std::vector<char> vecLine_;
    CViewCmd * pObj_;
public:
    CViewShell(CViewCmd * ptr);
    void Clear();
    std::string GetString();
    void HandlerTab();
    void HandlerBackspace();
    bool HandlerEnter();
    void HandlerChar();
    void Run();
};
#endif // VIEW_SHELL_H