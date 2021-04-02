#include <windows.h>
#include <stdio.h>

#define MAX_SEM_COUNT 10
#define THREADCOUNT 12

HANDLE ghSemaphore;

DWORD WINAPI ThreadProc(LPVOID);

void main()
{
    HANDLE aThread[THREADCOUNT];
    int ids[THREADCOUNT];
    DWORD ThreadID;
    int i;

    // Create a semaphore with initial and max counts of MAX_SEM_COUNT

    ghSemaphore = CreateSemaphore(
        NULL,           // default security attributes
        1,  // initial count
        MAX_SEM_COUNT,  // maximum count
        NULL);          // unnamed semaphore

    if (ghSemaphore == NULL)
    {
        printf("CreateSemaphore error: %d\n", GetLastError());
        return;
    }

    // Create worker threads

    for (i = 0; i < THREADCOUNT; i++)
    {
        ids[i] = i;
        aThread[i] = CreateThread(
            NULL,       // default security attributes
            0,          // default stack size
            (LPTHREAD_START_ROUTINE)ThreadProc,
            &ids[i],       // no thread function arguments
            0,          // default creation flags
            &ThreadID); // receive thread identifier

        if (aThread[i] == NULL)
        {
            printf("CreateThread error: %d\n", GetLastError());
            return;
        }
    }

    // Wait for all threads to terminate

    WaitForMultipleObjects(THREADCOUNT, aThread, TRUE, INFINITE);

    // Close thread and semaphore handles

    for (i = 0; i < THREADCOUNT; i++)
        CloseHandle(aThread[i]);

    CloseHandle(ghSemaphore);
}

DWORD WINAPI ThreadProc(LPVOID lpParam)
{
    DWORD dwWaitResult;
    BOOL bContinue = TRUE;
    int i = *(int *)lpParam;
    printf("index %d\n", i);
    while (bContinue)
    {
        // Try to enter the semaphore gate.

        /*dwWaitResult = WaitForSingleObject(
            ghSemaphore,   // handle to semaphore
            0L);           // zero-second time-out interval*/
        dwWaitResult = WaitForSingleObject(ghSemaphore, 60);

        switch (dwWaitResult)
        {
            // The semaphore object was signaled.
        case WAIT_OBJECT_0:
            // TODO: Perform task
            printf("*************Thread %d-%d: wait succeeded************\n", i, GetCurrentThreadId());
            bContinue = FALSE;

            // Simulate thread spending time on task
            Sleep(5);

            // Release the semaphore when task is finished

            if (!ReleaseSemaphore(
                ghSemaphore,  // handle to semaphore
                1,            // increase count by one
                NULL))       // not interested in previous count
            {
                printf("ReleaseSemaphore error: %d\n", GetLastError());
            }
            break;

            // The semaphore was nonsignaled, so a time-out occurred.
        case WAIT_TIMEOUT:
            printf("Thread %d-%d: wait timed out\n", i, GetCurrentThreadId());
            break;
        }
    }
    return TRUE;
}