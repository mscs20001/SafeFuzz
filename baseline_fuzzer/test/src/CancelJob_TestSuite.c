#include "Crypto.h"
#include "TestHarness.h"

/* Job configuration for SHA2_256 */

#define TESTCASE_DATA_LENGTH_0 (100U)

static Crypto_PrimitiveInfoType TestPrimitiveInfo_0 = {
    TESTCASE_DATA_LENGTH_0, /* resultLength */
    CRYPTO_HASH, /* service */
    {
        CRYPTO_ALGOFAM_SHA2_256, /* family */
        CRYPTO_ALGOFAM_NOT_SET, /* secondaryFamily (unused for SHA2_256) */
        0U, /* keyLength (unused for SHA2_256) */
        CRYPTO_ALGOMODE_NOT_SET, /* mode (unused for SHA2_256) */
    }, /* algorithm */
};

static Crypto_JobPrimitiveInfoType TestJobPrimitiveInfo_0 = {
    0U, /* callbackId (unused) */
    &TestPrimitiveInfo_0, /* primitiveInfo */
    0U, /* secureCounterId (unused) */
    0U, /* cryIfKeyId (unused) */
    CRYPTO_PROCESSING_SYNC, /* processingType */
    FALSE, /* callbackUpdateNotification (unused) */
};

static Crypto_JobInfoType TestJobInfo_0 = {
    0U, /* jobId */
    0U, /* jobPriority */
};

static uint8 TestInputPtr_0[TESTCASE_DATA_LENGTH_0];

static uint8 TestOutputPtr_0[256U / 8U];

static uint32 TestOutputLength_0 = 256U / 8U;

static Crypto_JobType TestJob_0 = {
    0U, /* jobId */
    CRYPTO_JOBSTATE_IDLE, /* jobState */
    {
        &TestInputPtr_0[0], /* inputPtr */
        TESTCASE_DATA_LENGTH_0, /* inputLength */
        NULL_PTR, /* secondaryInputPtr (unused in HASH) */
        0U, /* secondaryInputLength (unused in HASH) */
        NULL_PTR, /* tertiaryInputPtr (unused in HASH) */
        0U, /* tertiaryInputLength (unused in HASH) */
        &TestOutputPtr_0[0U], /* outputPtr */
        &TestOutputLength_0, /* outputLengthPtr */
        NULL_PTR, /* secondaryOutputPtr (unused in HASH) */
        NULL_PTR, /* secondaryOutputLengthPtr (unused in HASH) */
        0U, /* input64 (unused in HASH) */
        NULL_PTR, /* verifyPtr (unused in HASH) */
        NULL_PTR, /* output64Ptr (unused in HASH) */
        CRYPTO_OPERATIONMODE_SINGLECALL /* mode */
    }, /* jobPrimitiveInputOutput */
    &TestJobPrimitiveInfo_0, /* jobPrimitiveInfo */
    &TestJobInfo_0, /* jobInfo */
    CryptoConf_CryptoKey_TestKey_Unused, /* cryptoKeyId */
};

/*======================= TEST CASES' IMPLEMENTATION ========================*/

void CancelJob_TestSuite(void)
{
    uint32 ObjectId;
    uint8 DoInit;

    TestHarness_PrepareInput((void *)&ObjectId, 32);
    TestHarness_PrepareInput((void *)&DoInit, 1);

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    (void)Crypto_CancelJob(ObjectId, &TestJob_0);
}

/*=============== END OF FILE CancelJob_TestSuite.c ================*/
