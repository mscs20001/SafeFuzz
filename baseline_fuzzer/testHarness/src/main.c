
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

extern void cov_term(void);

void clean_exit_on_sig(int sig_num)
{
    cov_term();
    TestHarness_Teardown();
    exit(sig_num);
}

int main(int argc, char *argv[])
{
    int threadId;
    int testId;

    printf("\n================================================");
    printf("\n SVO (Safety & Vulnerability Oriented) Fuzzer");
    printf("\n================================================");
    printf("\n");

    // Signal types
    // ====================================
    // SIGINT          2   // interrupt
    // SIGILL          4   // illegal instruction - invalid function image
    // SIGFPE          8   // floating point exception
    // SIGSEGV         11  // segment violation
    // SIGTERM         15  // Software termination signal from kill
    // SIGBREAK        21  // Ctrl-Break sequence
    // SIGABRT         22  // abnormal termination triggered by abort call
    signal(SIGINT , clean_exit_on_sig);
    signal(SIGABRT , clean_exit_on_sig);
    signal(SIGILL , clean_exit_on_sig);
    signal(SIGFPE , clean_exit_on_sig);
    signal(SIGSEGV, clean_exit_on_sig);
    signal(SIGTERM , clean_exit_on_sig);

    TestHarness_PrepareInput((void *)&threadId, 32);
    TestHarness_Setup(threadId);
    TestHarness_PrepareInput((void *)&testId, 32);

    switch(testId)
    {
        case 0: AES_128_TestCase_0(); break;
        case 1: CancelJob_TestSuite(); break;
        case 2: CertificateParse_TestSuite(); break;
        case 3: CertificateVerify_TestSuite(); break;
        case 4: KeyCopy_TestSuite(); break;
        case 5: KeyDerive_TestSuite(); break;
        case 6: KeyElementCopy_TestSuite(); break;
        case 7: KeyElementGet_TestSuite(); break;
        case 8: KeyElementIdsGet_TestSuite(); break;
        case 9: KeyElementSet_TestSuite(); break;
        case 10: KeyExchangeCalcPubVal_TestSuite(); break;
        case 11: KeyExchangeCalcSecret_TestSuite(); break;
        case 12: KeyGenerate_TestSuite(); break;
        case 13: KeySetValid_TestSuite(); break;
        case 14: RandomSeed_TestSuite(); break;
        case 15: RNG_TestSuite(); break;
        default: printf("\n invalid testId=%d", testId); break;
    }
    printf("\n");
    printf("Done\n");
    TestHarness_Teardown();

    return 0;
}
