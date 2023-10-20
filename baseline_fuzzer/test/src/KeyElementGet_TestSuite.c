#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyElementGet_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId;
    uint32 KeyElementId;
    uint8 KeyElement[32];
    uint32 KeyElementLength;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId, 32);
    TestHarness_PrepareInput((void *)&KeyElementId, 32);
    TestHarness_PrepareInput((void *)&KeyElementLength, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_KeyElementGet(KeyId, KeyElementId, &KeyElement[0], &KeyElementLength);
}

/*=============== END OF FILE KeyElementGet_TestSuite.c ================*/
