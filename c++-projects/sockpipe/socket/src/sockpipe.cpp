#include <stdio.h>
#include <WinSock2.h>
#include <process.h>
#include <windows.h>

#include "blog.h"
//#include <iostream>
//#include <map>
#include "sockpipe.h"

#pragma comment(lib,"WS2_32.lib") //显式连接套接字
#define _WINSOCK_DEPRECATED_NO_WARNINGS

unsigned int __stdcall runpipe(void* pPara);
unsigned int __stdcall runserver(void* pPara);
unsigned int __stdcall runclient(void* pPara);

typedef struct sockpipe {
	HANDLE semOrder;
	HANDLE semCtrl;
    HANDLE evtShutdown;

	HANDLE server;
	HANDLE client;
    HANDLE spipe;

    SOCKET sockSend;

    int port;
    bool running;

    int (*filldata)(void*, int);

	int Run()
	{
        running = true;
        spipe = (HANDLE)_beginthreadex(NULL, 0, runpipe, this, 0, NULL);
        if (!spipe) {
            blog(LOG_ERROR, "server start failed!\n");
            running = false;
            return -1;
        }
        return 0;
	}

    int write(char * str, unsigned int len){ return send(sockSend, str, len + sizeof(char), NULL); }

    void Stop()
    {
        WaitForSingleObject(semCtrl, INFINITE);
        running = false;
        ReleaseSemaphore(semCtrl, 1, NULL);

        SetEvent(evtShutdown);

        WaitForSingleObject(spipe, INFINITE); 
        CloseHandle(spipe);
    }

    bool IsRunning()
    {
        WaitForSingleObject(semCtrl, INFINITE);
        bool r = running;
        ReleaseSemaphore(semCtrl, 1, NULL);
        return r;
    }
} sockpipe_t;

unsigned int __stdcall runpipe(void* pPara)
{
    if (!pPara) {
        blog(LOG_ERROR, "runserver parameter is NULL");
        return 1;
    }
    sockpipe_t* pipe = (sockpipe_t*)pPara;

    int ret = 0;
    pipe->semOrder = CreateSemaphore(NULL, 0, 1, NULL);
    if (!pipe->semOrder) { blog(LOG_ERROR, "CreateSemaphore semOrder failed!\n"); ret = -1; goto CLEAN_END; }
    pipe->evtShutdown = CreateEvent(NULL, FALSE, FALSE, NULL);
    if (!pipe->evtShutdown) { blog(LOG_ERROR, "CreateEvent evtShutdown failed!\n"); ret = -2; goto CLEAN_ORD; }
    pipe->semCtrl = CreateSemaphore(NULL, 1, 1, NULL);
    if (!pipe->semCtrl) { blog(LOG_ERROR, "CreateSemaphore semCtrl failed!\n"); ret = -3; goto CLEAN_SHT; }

    pipe->server = (HANDLE)_beginthreadex(NULL, 0, runserver, pipe, 0, NULL);
    if (!pipe->server) { blog(LOG_ERROR, "server start failed!\n"); ret = -4; goto CLEAN_CTL; }
    WaitForSingleObject(pipe->semOrder, INFINITE);
    pipe->client = (HANDLE)_beginthreadex(NULL, 0, runclient, pipe, 0, NULL);
    if (!pipe->client) { blog(LOG_ERROR, "client start failed!\n"); ret = -5; goto CLEAN_SRV; }

    WaitForSingleObject(pipe->client, INFINITE);
    WaitForSingleObject(pipe->server, INFINITE);

    //关闭套接字
    closesocket(pipe->sockSend);
    //终止使用 DLL
    WSACleanup();

    CloseHandle(pipe->client);
CLEAN_SRV:
    CloseHandle(pipe->server);
CLEAN_CTL:
    CloseHandle(pipe->semCtrl);
CLEAN_SHT:
    CloseHandle(pipe->evtShutdown);
CLEAN_ORD:
    CloseHandle(pipe->semOrder);
CLEAN_END:
    blog(LOG_INFO, "pipe thread exit\n");
    return ret;
}
unsigned int __stdcall runserver(void* pPara)
{
    if (!pPara) {
        blog(LOG_ERROR, "runserver parameter is NULL");
        return 1;
    }

    sockpipe_t* pipe = (sockpipe_t*)pPara;
    //初始化 DLL
    WSADATA wsaData;
    int ret = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (ret < 0) {
        blog(LOG_ERROR, "WSAStartup failed!%d\n", ret);
        return 2;
    }
    //创建套接字
    SOCKET servSock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
    //绑定套接字
    sockaddr_in sockAddr;
    memset(&sockAddr, 0, sizeof(sockAddr));  //每个字节都用0填充
    sockAddr.sin_family = PF_INET;  //使用IPv4地址
    sockAddr.sin_addr.s_addr = inet_addr("127.0.0.1");  //具体的IP地址
    sockAddr.sin_port = htons(pipe->port);  //端口
    bind(servSock, (SOCKADDR*)&sockAddr, sizeof(SOCKADDR));
    //进入监听状态
    listen(servSock, 20);

    //释放客户端可以启动的信号
    ReleaseSemaphore(pipe->semOrder, 1, NULL);

    //接收客户端请求
    SOCKADDR clntAddr;
    int nSize = sizeof(SOCKADDR);
    SOCKET clntSock = accept(servSock, (SOCKADDR*)&clntAddr, &nSize);

    //接收服务器传回的数据
    char szBuffer[MAXBYTE] = { 0 };

    while (true) {
        int rlen = recv(clntSock, szBuffer, MAXBYTE, NULL);
        //输出接收到的数据
        //printf("Message form client(%d): %s\n", rlen, szBuffer);
        if (pipe->filldata && rlen > 0) pipe->filldata(szBuffer, rlen);

        //是否关闭
        if (!pipe->IsRunning()) break;
    }

    //关闭套接字
    closesocket(clntSock);
    closesocket(servSock);
    //终止 DLL 的使用
    //WSACleanup();
    blog(LOG_INFO, "server thread exit\n");
    return 0;
}
unsigned int __stdcall runclient(void* pPara)
{
    if (!pPara) {
        blog(LOG_ERROR, "runserver parameter is NULL");
        return 1;
    }

    sockpipe_t* pipe = (sockpipe_t*)pPara;
    //初始化DLL
    WSADATA wsaData;
    int ret = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if( ret < 0) {
        blog(LOG_ERROR, "WSAStartup failed!%d\n", ret);
        return 2;
    }
    //创建套接字
    pipe->sockSend = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
    //向服务器发起请求
    sockaddr_in sockAddr;
    memset(&sockAddr, 0, sizeof(sockAddr));  //每个字节都用0填充
    sockAddr.sin_family = PF_INET;
    sockAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    sockAddr.sin_port = htons(pipe->port);
    connect(pipe->sockSend, (SOCKADDR*)&sockAddr, sizeof(SOCKADDR));

    //等待结束
    WaitForSingleObject(pipe->evtShutdown, INFINITE);
    send(pipe->sockSend, "0", 2, NULL); //触发server结束

    blog(LOG_INFO, "client thread exit\n");
    return 0;
}

CellPipe::CellPipe(int port, int (*f)(void*, int))
{
    pipe = new sockpipe_t();
    sockpipe_t* ptr = (sockpipe_t*)pipe;
    ptr->port = port;
    ptr->filldata = f;
    running = false;
}

CellPipe::~CellPipe()
{
    sockpipe_t* ptr = (sockpipe_t*)pipe;
    Stop();
    delete(ptr);
    pipe = ptr = NULL;
}

int CellPipe::Start()
{
    sockpipe_t* ptr = (sockpipe_t*)pipe;
    int r = ptr->Run();
    if (r == 0) running = true;
    return r;
}

int CellPipe::Write(char* data, int len)
{
    sockpipe_t* ptr = (sockpipe_t*)pipe;
    return ptr->write(data, len);
}

void CellPipe::Stop()
{
    if (running) {
        sockpipe_t* ptr = (sockpipe_t*)pipe;
        running = false;
        ptr->Stop();
    }
}

/*std::map<int, sockpipe_t*> mapPipes;
sockpipe_t* NewPipe(int port)
{
    std::map<int, sockpipe_t*>::iterator l_it;;
    l_it = mapPipes.find(port);
    if (l_it != mapPipes.end())
        return NULL;
    mapPipes[port] = new sockpipe_t();
    return mapPipes[port];
}

sockpipe_t* FindPipe(int port)
{
    std::map<int, sockpipe_t*>::iterator l_it;;
    l_it = mapPipes.find(port);
    if (l_it == mapPipes.end())
        return NULL;
    return mapPipes[port];
}

extern "C" int pipe_start(int (*f)(void*, int), int port)
{
    sockpipe_t *sp = NewPipe(port);
    sp->port = port; sp->filldata = f;
    return sp->Run();
}
extern "C" int pipe_write(char * data, int len, int port)
{
    sockpipe_t* sp = FindPipe(port);
    return sp->write(data, len);
}
extern "C" void pipe_stop(int port)
{
    sockpipe_t* sp = FindPipe(port);
    sp->Stop();
}*/