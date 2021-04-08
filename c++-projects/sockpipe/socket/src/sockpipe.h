#pragma once

/*#ifdef __cplusplus
extern "C" {
#endif

extern int pipe_start(int (*f)(void*, int), int port);
extern int pipe_write(char* data, int len, int port);
extern "C" void pipe_stop(int port);

#ifdef __cplusplus
}
#endif*/

class CellPipe {
public:
	CellPipe(int port, int (*f)(void*, int));
	~CellPipe();

	int Start();
	int Write(char* data, int len);
	void Stop();
private:
	void* pipe;
	bool running;
};