#pragma once

#include <process.h>
#include <windows.h>
#include <string>

/*template <typename T>
class CPipe {
public:
	CPipe(T p) : pipe(p) {}
	~CPipe() {}
	int Start() { return pipe.Start(); }
	void Stop() { pipe.Stop(); }
	int Recive(void* buf, size_t len) { return pipe.Recive(buf, len); }
	int Send(const void* buf, size_t len) { return pipe.Send(buf, len); }
private:
	T pipe;
};*/

enum
{
	PIPE_SERVER = 0,
	PIPE_CLIENT,
	PIPE_LOCAL,
	PIPE_INVALID
};

class CPipe {
public:
	CPipe(int t, int p, std::string ip = "127.0.0.1");
	~CPipe();
	int Run();
	void Stop();
	int Recive(char* buf, size_t len);
	int Send(const char* buf, size_t len);
	
private:
	void net_init();
	void net_clean();
	bool valid();

private:
	//server
	void* acceptThread;
	unsigned int srv_sock_local;
	unsigned int srv_sock_remote;
	bool srv_started = false;

	int srv_start();
	void srv_stop();
	static unsigned int __stdcall accept_pro(void* pPara);
	bool srv_valid();
	int srv_recive(char* buf, size_t len);
	int srv_send(const char* buf, size_t len);

private:
	//client
	void* connectThread;
	unsigned int cln_sock;
	bool cln_connected = false;
	int cln_start();
	void cln_stop();
	static unsigned int __stdcall connect_pro(void* pPara);
	bool cln_valid();
	int cln_recive(char* buf, size_t len);
	int cln_send(const char* buf, size_t len);

private:
	//local pipe
	void* semOrder;

private:
	std::string addr;
	int type;
	int port;

};