#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyDerive_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId_0;
    uint32 KeyId_1;

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

    Crypto_KeyDerive(KeyId_0, KeyId_1);
}
/*=============== END OF FILE KeyDerive_TestSuite.c ================*/
