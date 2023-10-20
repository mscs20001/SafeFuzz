#include "Std_Types.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "CryIf.h"
#include "Det.h"
#include "SchM_Crypto.h"
#include "mbedtls/entropy_poll.h"

#define INPUT_BUFFER_SIZE (1024 * 1024)
uint8 inBuf[INPUT_BUFFER_SIZE] = {0};

void TestHarness_PrepareInput(void * inPtr, uint8 size)
{
    char *ptr;
    printf("TestHarness_PrepareInput\n");
    (void)fgets(inBuf, INPUT_BUFFER_SIZE , stdin);
    switch (size)
    {
        case 1: *(boolean *)inPtr = strtoul(inBuf, &ptr, 10); break;
        case 8: *(uint8 *)inPtr = strtoul(inBuf, &ptr, 10); break;
        case 16: *(uint16 *)inPtr = strtoul(inBuf, &ptr, 10); break;
        case 32: *(uint32 *)inPtr = strtoul(inBuf, &ptr, 10); break;
        case 64: *(uint64 *)inPtr = strtoull(inBuf, &ptr, 10); break;
        default: break;
    }
}

static FILE *fp_trace;

void TestHarness_Setup(uint32 runId)
{
    char traceFilename[64];
    snprintf(traceFilename, 64, "out/trace_%d.out", runId);
    fp_trace = fopen(traceFilename, "w");
}

void TestHarness_Teardown(void)
{
    fclose(fp_trace);
}

void __cyg_profile_func_enter(void *func,  void *caller)
{
    fprintf(fp_trace, "ENTER:0x%p\n", func);
}
 
void __cyg_profile_func_exit(void *func, void *caller)
{
    fprintf(fp_trace, "EXIT:0x%p\n", func);
}

