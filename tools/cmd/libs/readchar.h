#ifndef READCHAR_H
#define READCHAR_H
#include <stdio.h>
#include <conio.h>
#include <string>
#include <vector>

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
        printf("\b \b\0");
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
            cGet_ = getch();
            Handler();
        }
    }
};
#endif // READCHAR_H