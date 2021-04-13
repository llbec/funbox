#include "netpipe.h"
#include "blog.h"
#include <WinSock2.h>
#include <process.h>
#include <windows.h>

const int g_backlog = 10;

CPipe::CPipe(int t, int p, std::string ip = "127.0.0.1") : type(t), port(p), ipaddr(ip) { net_init(); }

CPipe::~CPipe() { net_clean(); }

void CPipe::net_init()
{
    WSADATA wsa;
    int res = WSAStartup(MAKEWORD(2, 2), &wsa) < 0;
    if (res < 0) {
        blog(LOG_ERROR, "WSAStartup failed with error %d\n", res);
    }
}

void CPipe::net_clean() { WSACleanup(); }

int CPipe::srv_start()
{
    int ret = 0;
    //创建套接字
    srv_sock_local = socket(AF_INET, SOCK_STREAM, 0);
    if (srv_sock_local == INVALID_SOCKET) {
        blog(LOG_ERROR, "sock_srv_local INVALID_SOCKET\n");
        return -1;
    }

    //绑定套接字
    SOCKADDR_IN sin;
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = inet_addr(ipaddr.c_str());
    sin.sin_port = htons(port);

    if (bind(srv_sock_local, (SOCKADDR*)&sin, sizeof(sin)) == SOCKET_ERROR) {
        blog(LOG_ERROR, "sock_srv_local bind faild\n");
        ret = -2;
        goto SOCK_CLOSE;
    }

    //打开监听
    if (listen(srv_sock_local, g_backlog) == SOCKET_ERROR) {
        blog(LOG_ERROR, "sock_srv_local listen faild\n");
        ret = -3;
        goto SOCK_CLOSE;
    }

    if (type == PIPE_LOCAL) {
        //释放客户端可以启动的信号
        ReleaseSemaphore(semOrder, 1, NULL);
    }

    //等待连接请求-子线程
    acceptThread = (HANDLE)_beginthreadex(NULL, 0, accept_pro, this, 0, NULL);

    return 0;

SOCK_CLOSE:
    closesocket(srv_sock_local);
    return ret;
}

void CPipe::srv_stop()
{
    WaitForSingleObject(acceptThread, INFINITE);
    CloseHandle(acceptThread);
    closesocket(srv_sock_remote);
    closesocket(srv_sock_local);
    srv_started = false;
}

unsigned int __stdcall CPipe::accept_pro(void* pPara)
{
    CPipe* pipe = (CPipe*)pPara;

    SOCKADDR clntAddr;
    int nSize = sizeof(SOCKADDR);
    pipe->srv_sock_remote = accept(pipe->srv_sock_local, (SOCKADDR*)&clntAddr, &nSize);
    pipe->srv_started = true;
    return 0;
}

int CPipe::srv_recive(char* buf, size_t len)
{
    if(!srv_started){
        return 0;
    }
    return recv(srv_sock_remote, buf, len, 0);
}

int CPipe::srv_send(const char* buf, size_t len)
{
    if (!srv_started) {
        return 0;
    }
    return send(srv_sock_remote, buf, len, 0);
}

int CPipe::cln_start()
{
    int ret = 0;
    //创建套接字
    cln_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (cln_sock == INVALID_SOCKET) {
        blog(LOG_ERROR, "sock_srv_local INVALID_SOCKET\n");
        return -1;
    }

    if (type == PIPE_LOCAL) {
        //等待客户端可以启动的信号
        WaitForSingleObject(semOrder, INFINITE);
    }

    //发起连接请求-子线程
    connectThread = (HANDLE)_beginthreadex(NULL, 0, connect_pro, this, 0, NULL);
    return 0;
}

void CPipe::cln_stop()
{
    WaitForSingleObject(connectThread, INFINITE);
    CloseHandle(connectThread);
    closesocket(cln_sock);
    cln_connected = false;
}

unsigned int __stdcall CPipe::connect_pro(void* pPara)
{
    CPipe* pipe = (CPipe*)pPara;

    //连接套接字
    SOCKADDR_IN sin;
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = inet_addr(pipe->ipaddr.c_str());
    sin.sin_port = htons(pipe->port);
    while (true) {
        if (connect(pipe->cln_sock, (SOCKADDR*)&sin, sizeof(sin)) != SOCKET_ERROR) {
            pipe->cln_connected = true;
            return 0;
        }
        blog(LOG_WARNING, "client connect failed!\n");
    }
    return 0;
}

int CPipe::Run()
{}