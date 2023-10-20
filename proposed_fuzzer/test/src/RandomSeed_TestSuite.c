#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void RandomSeed_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId;
    uint8 Seed[16] = {0};
    uint32 SeedLength;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId, 32);
    TestHarness_PrepareInput((void *)&SeedLength, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_RandomSeed(KeyId, &Seed[0], SeedLength);
}

/*=============== END OF FILE RandomSeed_TestSuite.c ================*/
