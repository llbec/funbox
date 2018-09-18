#ifndef READCHAR_H
#define READCHAR_H
#include <stdio.h>
#include <string>
#include <vector>

/*
 * __GNUC        => linux
 * __MSC_VER    => window
 */
#ifdef __GNUC__  // depend on GCC

#include <termio.h>
/*
 * get one char from  input
 * return: char
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

#elif _MSC_VER // depend on Visual Studio

#include <conio.h>
#define sh_getch    _getch

#else
    #error "error : Currently only supports the Visual Studio and GCC!"
#endif

template<class Type>
class CReadChar
{
private:
    bool bTab_;
    char cGet_;
    Type * ptrObj_;
    std::vector<char> vecLine_;
public:
    CReadChar(Type* obj) : bTab_(false), cGet_('\0'), ptrObj_(obj) {}

    void Clear() {
        bTab_ = false;
        cGet_ = '\0';
        vecLine_.clear();
    }

    std::string ToString() {
        std::string sLine;
        sLine.insert(sLine.begin(), vecLine_.begin(), vecLine_.end());
        return sLine;
    }

    void HandlerTab() {
        if(bTab_) {
            std::vector<std::string> vecOpt;
            ptrObj_->GetPossible(vecOpt, ToString());
            printf("\n");
            for(auto var : vecOpt)
                printf("%s\t", var.c_str());
            printf("\n%s", ToString().c_str());
        } else {
            std::vector<char> vecWord;
            ptrObj_->GetWord(vecWord, ToString());
            for(auto var : vecWord)
            {
                vecLine_.push_back(var);
                printf("%c", var);
            }
            bTab_ = false;
        }
    }

    void HandlerBacksoace() {
        vecLine_.pop_back();
        bTab_ = false;
        printf("\b \b%c",'\0');
    }

    void HandlerEnter() {
        ptrObj_->Handler(ToString());
        printf("\n");
        Clear();
    }

    void HandlerChar() {
        vecLine_.push_back(cGet_);
        bTab_ = false;
        printf("%c", cGet_);
    }

    void Handler(){
        if(cGet_ == '\0')
            return;
        else if(cGet_ == '\t')
            HandlerTab();
        else if(cGet_ == '\b')
            HandlerBacksoace();
        else if(cGet_ == '\r')
            HandlerEnter();
        else
            HandlerChar();
        cGet_ = '\0';
    }

    void Run(){
        while(true){
            cGet_ = sh_getch();
            Handler();
        }
    }
};
#endif // READCHAR_H
