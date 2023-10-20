#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/
void CertificateVerify_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId_0;
    uint32 KeyId_1;
    Crypto_VerifyResultType Result;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId_0, 32);
    TestHarness_PrepareInput((void *)&KeyId_1, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_CertificateVerify(KeyId_0, KeyId_1, &Result);
}

/*=============== END OF FILE CertificateVerify_TestSuite.c ================*/
