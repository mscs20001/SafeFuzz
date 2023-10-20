#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyExchangeCalcPubVal_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId;
    uint8 OwnPublicValue[32];
    uint32 OwnPublicValueLength;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId, 32);
    TestHarness_PrepareInput((void *)&OwnPublicValueLength, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_KeyExchangeCalcPubVal(KeyId, &OwnPublicValue[0], &OwnPublicValueLength);
}

/*=============== END OF FILE KeyExchangeCalcPubVal_TestSuite.c ================*/
