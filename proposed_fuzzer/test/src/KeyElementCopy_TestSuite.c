#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyElementCopy_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId_0;
    uint32 KeyElementId_0;
    uint32 KeyId_1;
    uint32 KeyElementId_1;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId_0, 32);
    TestHarness_PrepareInput((void *)&KeyElementId_0, 32);
    TestHarness_PrepareInput((void *)&KeyId_1, 32);
    TestHarness_PrepareInput((void *)&KeyElementId_1, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_KeyElementCopy(KeyId_0, KeyElementId_0, KeyId_1, KeyElementId_1);
}
/*=============== END OF FILE KeyElementCopy_TestSuite.c ================*/
