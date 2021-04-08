// socket.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include<iostream>
#include"src/sockpipe.h"

int output(void* buf, int len)
{
    printf("Message form client(%d): %s\n", len, (char *)buf);
    return 0;
}

int main()
{
    int port = 6960;
    CellPipe pipe(port, output);
    pipe.Start();

    char str[20] = { NULL };
    std::cin.getline(str, 20);
    while (strcmp(str, "quit")!=0) {
        //send(pipe->sockSend, str, strlen(str) + sizeof(char), NULL);
        int n = strlen(str);
        char* tmp = new char[n * 100000];
        for(int i = 0; i < 100000; i++){
            memcpy(tmp + (i * n), str, n);
        }
        pipe.Write(tmp, n* 100000);
        memset(str, 0, 20);
        std::cin.getline(str, 20);
    }
    pipe.Stop();
    return 0;
}

// 运行程序: Ctrl + F5 或调试 >“开始执行(不调试)”菜单
// 调试程序: F5 或调试 >“开始调试”菜单

// 入门使用技巧: 
//   1. 使用解决方案资源管理器窗口添加/管理文件
//   2. 使用团队资源管理器窗口连接到源代码管理
//   3. 使用输出窗口查看生成输出和其他消息
//   4. 使用错误列表窗口查看错误
//   5. 转到“项目”>“添加新项”以创建新的代码文件，或转到“项目”>“添加现有项”以将现有代码文件添加到项目
//   6. 将来，若要再次打开此项目，请转到“文件”>“打开”>“项目”并选择 .sln 文件