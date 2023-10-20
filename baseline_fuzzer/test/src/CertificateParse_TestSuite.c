#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void CertificateParse_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }
    
    Crypto_CertificateParse(KeyId);
}

/*=============== END OF FILE CertificateParse_TestSuite.c ================*/
