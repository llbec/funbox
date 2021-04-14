#include "netpipe.h"
#include "blog.h"
//#include <WinSock2.h>

#pragma comment(lib,"WS2_32.lib") //显式连接套接字
#define _WINSOCK_DEPRECATED_NO_WARNINGS

const int g_backlog = 10;

CPipe::CPipe(int t, int p, std::string ip) : type(t), port(p), addr(ip) { net_init(); }

CPipe::~CPipe() { if(valid()) Stop(); }

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
    srv_sock_local = (unsigned int)socket(AF_INET, SOCK_STREAM, 0);
    if (srv_sock_local == INVALID_SOCKET) {
        blog(LOG_ERROR, "sock_srv_local INVALID_SOCKET\n");
        return -1;
    }

    //绑定套接字
    SOCKADDR_IN sin;
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = inet_addr(addr.c_str());
    sin.sin_port = htons(port);

    int r = bind(srv_sock_local, (SOCKADDR*)&sin, sizeof(sin));
    if (r < 0) {
        blog(LOG_ERROR, "sock_srv_local bind faild\n%d\n", WSAGetLastError());
        ret = -2;
        goto SOCK_CLOSE;
    }

    //打开监听
    if (listen(srv_sock_local, g_backlog) < 0) {
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
    pipe->srv_sock_remote = (unsigned int)accept(pipe->srv_sock_local, (SOCKADDR*)&clntAddr, &nSize);
    pipe->srv_started = true;
    return 0;
}

bool CPipe::srv_valid()
{
    if (!srv_started || srv_sock_remote == INVALID_SOCKET)
        return false;
    return true;
}

int CPipe::srv_recive(char* buf, size_t len)
{
    if (!srv_valid()) return 0;
    return recv(srv_sock_remote, buf, len, 0);
}

int CPipe::srv_send(const char* buf, size_t len)
{
    if (!srv_valid()) return 0;
    return send(srv_sock_remote, buf, len, 0);
}

int CPipe::cln_start()
{
    int ret = 0;
    //创建套接字
    cln_sock = (unsigned int)socket(AF_INET, SOCK_STREAM, 0);
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
    sin.sin_addr.s_addr = inet_addr(pipe->addr.c_str());
    sin.sin_port = htons(pipe->port);
    while (true) {
        if (connect(pipe->cln_sock, (SOCKADDR*)&sin, sizeof(sin)) >= 0) {
            pipe->cln_connected = true;
            return 0;
        }
        blog(LOG_WARNING, "client connect failed!\n");
    }
    return 0;
}

bool CPipe::cln_valid()
{
    if (!cln_connected || cln_sock == INVALID_SOCKET)
        return false;
    return true;
}

int CPipe::cln_recive(char* buf, size_t len)
{
    if (!cln_valid()) return 0;
    return recv(cln_sock, buf, len, 0);
}

int CPipe::cln_send(const char* buf, size_t len)
{
    if (!cln_valid()) return 0;
    return send(cln_sock, buf, len, 0);
}

int CPipe::Run()
{
    net_init();
    int ret = 0;
    if (type != PIPE_CLIENT) {
        if (type == PIPE_LOCAL) {
            semOrder = CreateSemaphore(NULL, 0, 1, NULL);
            if (!semOrder) { blog(LOG_ERROR, "CreateSemaphore semOrder failed!\n"); ret = -1; goto CLEAN_NET; }
        }
        if (srv_start() < 0) { ret = -2; goto CLEAN_NET; }
    }
    if (type != PIPE_SERVER) {
        if (cln_start() < 0) { ret = -2; goto CLEAN_NET; }
    }
    return 0;

CLEAN_NET:
    net_clean();
    return ret;
}

void CPipe::Stop()
{
    if (type != PIPE_CLIENT) srv_stop();
    if (type != PIPE_SERVER) cln_stop();
    if (type == PIPE_LOCAL) CloseHandle(semOrder);
    net_clean();
}

bool CPipe::valid()
{
    if (type == PIPE_SERVER) return srv_valid();
    else if (type == PIPE_CLIENT) return cln_valid();
    else return srv_valid() && cln_valid();
}

int CPipe::Recive(char* buf, size_t len)
{
    if (type == PIPE_SERVER) return srv_recive(buf, len);
    else return cln_recive(buf, len);
}
int CPipe::Send(const char* buf, size_t len)
{
    if (type != PIPE_CLIENT) return srv_send(buf, len);
    else return cln_send(buf, len);
}