#include <stdio.h>
#include <iostream>
#include "netpipe.h"
#include "blog.h"
#include "buffer_util.h"

//CPipe pipe(PIPE_LOCAL, 6960);
PipeServer server(6960);
PipeClient client(6960);
HANDLE semio;
bool isStop = true;

unsigned int __stdcall rcv_pro(void* pPara);
unsigned int __stdcall send_pro(void* pPara);

int main()
{
	int ret = 0;
	HANDLE hrcv;
	HANDLE hsend;
	

	if (server.Start() < 0) { ret = -1; goto END_RET; }
	if (client.Start() < 0) { ret = -1; goto END_RET; }

	isStop = false;
	semio = CreateSemaphore(NULL, 1, 1, NULL);
	hrcv = (HANDLE)_beginthreadex(NULL, 0, rcv_pro, &server, 0, NULL);
	if (!hrcv) { blog(LOG_ERROR, "server start failed!\n"); ret = -2; goto END_STOP; }
	hsend = (HANDLE)_beginthreadex(NULL, 0, send_pro, &client, 0, NULL);
	if (!hsend) { blog(LOG_ERROR, "server start failed!\n"); ret = -3; goto CLEAN_CTL; }

	WaitForSingleObject(hsend, INFINITE);
	WaitForSingleObject(hrcv, INFINITE);
	CloseHandle(hsend);
CLEAN_CTL:
	CloseHandle(hrcv);
END_STOP:
	CloseHandle(semio);
	client.Stop();
	server.Stop();
END_RET:
	return ret;
}

#define MAX_BUF_LEN  65535

unsigned int __stdcall rcv_pro(void* pPara)
{
	PipeServer* ptr = (PipeServer*)pPara;
	uint8_t header[12];
	
	while (true) {
		memset(header, 0, 12);
		int r = ptr->Recive((char*)header, 12);
		if (r == 0) {
			blog(LOG_INFO, "rcv 0");
			continue;
		}
		uint64_t pts = buffer_read64be(header);
		uint32_t len = buffer_read32be(&header[8]);
		char* data = new char[len];
		r = ptr->Recive((char*)data, len);
		while (r < len) {
			blog(LOG_INFO, "rcv continue! expected:%d, facted:%d\n", len, r);
			//continue;
			r += ptr->Recive((char*)data+r, len-r);
		}
		WaitForSingleObject(semio, INFINITE);
		//std::cout << "recive msg(" << r << "): " << data << std::endl;
		printf("recive msg. header len:%d, rcv:%d\n", len, r);
		ReleaseSemaphore(semio, 1, NULL);
		if (strcmp(data, "quit") == 0) {
			break;
		}
		delete[] data;
	}
	return 0;
}

unsigned int __stdcall send_pro(void* pPara)
{
	PipeClient* ptr = (PipeClient*)pPara;
	char* str = new char[MAX_BUF_LEN];
	uint8_t hdr[12];
	while (true) {
		memset(str, 0, MAX_BUF_LEN);
		memset(hdr, 0, 12);
		std::cin >> str;
		int n = strlen(str);
		int tmplen = 1 + (n * 10000);
		char* tmp = new char[tmplen];
		memset(tmp, 0, tmplen);
		for (int i = 0; i < 10000; i++) {
			memcpy(&tmp[n*i], str, n);
		}

		int len = strlen(tmp) + 1;
		buffer_write64be(&hdr[0], 0xabcd);
		buffer_write32be(&hdr[8], len);
		int r = ptr->Send((char*)hdr, 12);
		r = ptr->Send(tmp, len);
		delete[] tmp;
		WaitForSingleObject(semio, INFINITE);
		//std::cout << "send msg " << r << len << tmplen << std::endl;
		printf("send msg: init:%d, cpy:%d, send:%d\n", tmplen, len, r);
		ReleaseSemaphore(semio, 1, NULL);
		if (strcmp(str, "quit") == 0) {
			break;
		}
	}
	delete[] str;
	return 0;
}
