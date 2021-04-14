#include <stdio.h>
#include <iostream>
#include "netpipe.h"
#include "blog.h"

CPipe pipe(PIPE_LOCAL, 6960);
HANDLE semio;

unsigned int __stdcall rcv_pro(void* pPara);
unsigned int __stdcall send_pro(void* pPara);

int main()
{
	int ret = 0;
	HANDLE hrcv;
	HANDLE hsend;
	

	if (pipe.Run() < 0) { ret = -1; goto END_RET; }

	semio = CreateSemaphore(NULL, 1, 1, NULL);
	hrcv = (HANDLE)_beginthreadex(NULL, 0, rcv_pro, &pipe, 0, NULL);
	if (!hrcv) { blog(LOG_ERROR, "server start failed!\n"); ret = -2; goto END_STOP; }
	hsend = (HANDLE)_beginthreadex(NULL, 0, send_pro, &pipe, 0, NULL);
	if (!hsend) { blog(LOG_ERROR, "server start failed!\n"); ret = -3; goto CLEAN_CTL; }

	WaitForSingleObject(hsend, INFINITE);
	WaitForSingleObject(hrcv, INFINITE);
	CloseHandle(hsend);
CLEAN_CTL:
	CloseHandle(hrcv);
END_STOP:
	CloseHandle(semio);
	pipe.Stop();
END_RET:
	return ret;
}

unsigned int __stdcall rcv_pro(void* pPara)
{
	CPipe* ptr = (CPipe*)pPara;
	char str[20] = { NULL };
	while (true) {
		int r = ptr->Recive(str, 20);
		WaitForSingleObject(semio, INFINITE);
		std::cout << "recive msg(" << r << "): " << str << std::endl;
		ReleaseSemaphore(semio, 1, NULL);
		memset(str, 0, 20);
	}
}
unsigned int __stdcall send_pro(void* pPara)
{
	CPipe* ptr = (CPipe*)pPara;
	char str[20] = { NULL };
	while (true) {
		std::cin >> str;
		int r = ptr->Send(str, strlen(str));
		WaitForSingleObject(semio, INFINITE);
		std::cout << "send msg " << r << std::endl;
		ReleaseSemaphore(semio, 1, NULL);
		memset(str, 0, 20);
	}
}