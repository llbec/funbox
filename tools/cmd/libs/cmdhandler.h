#ifndef CMDHANDLER_H
#define CMDHANDLER_H
#include <string>
#include <vector>

class CCmdHandler
{
public:
    CCmdHandler() {}
    void Handler(std::string str) {}
    void GetPossible(std::vector<std::string>& vecRet, std::string str) {}
    void GetWord(std::vector<char>& vecRet, std::string str) {}
};
#endif // CMDHANDLER_H