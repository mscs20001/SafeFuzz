#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyElementIdsGet_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId;
    uint32 keyElementIds[10];
    uint32 keyElementIdsLength;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId, 32);
    TestHarness_PrepareInput((void *)&keyElementIdsLength, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_KeyElementIdsGet(KeyId, &keyElementIds[0], &keyElementIdsLength);
}

/*=============== END OF FILE KeyElementIdsGet_TestSuite.c ================*/
