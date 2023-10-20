#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void KeyExchangeCalcSecret_TestSuite(void)
{
    uint8 DoInit;
    uint32 KeyId;
    uint8 PartnerPublicValue[32];
    uint32 PartnerPublicValueLength = 32U;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&KeyId, 32);
    TestHarness_PrepareInput((void *)&PartnerPublicValueLength, 32);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_KeyExchangeCalcSecret(KeyId, &PartnerPublicValue[0], PartnerPublicValueLength);
}

/*=============== END OF FILE KeyExchangeCalcSecret_TestSuite.c ================*/
