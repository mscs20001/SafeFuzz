#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyGenerate_TestSuite(void)
{
    uint8 Seed[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
    uint32 SeedLength;
    uint8 DoInit;
    uint8 DoSeed;
    uint32 KeyId_0;
    uint32 KeyId_1;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&DoSeed, 1);
    TestHarness_PrepareInput((void *)&KeyId_0, 32);
    TestHarness_PrepareInput((void *)&KeyId_1, 32);
    TestHarness_PrepareInput((void *)&SeedLength, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    if(DoSeed == 1)
    {
        Crypto_RandomSeed(KeyId_0, &Seed[0], SeedLength);
    }

    Crypto_KeyGenerate(KeyId_1);
}

/*=============== END OF FILE KeyGenerate_TestSuite.c ================*/
