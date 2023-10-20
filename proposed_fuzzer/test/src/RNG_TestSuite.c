#include "Crypto.h"
#include "TestHarness.h"

/*======================= TEST CASES' IMPLEMENTATION ========================*/

/* Job configuration */

static Crypto_PrimitiveInfoType TestPrimitiveInfo = {
    0U, /* resultLength */
    CRYPTO_RANDOMGENERATE, /* service */
    {
        CRYPTO_ALGOFAM_RNG, /* family */
        CRYPTO_ALGOFAM_NOT_SET, /* secondaryFamily (unused for RNG) */
        0U, /* keyLength (unused for RNG) */
        CRYPTO_ALGOMODE_NOT_SET, /* mode (unused for RNG) */
    }, /* algorithm */
};

static Crypto_JobPrimitiveInfoType TestJobPrimitiveInfo = {
    0U, /* callbackId (unused) */
    &TestPrimitiveInfo, /* primitiveInfo */
    0U, /* secureCounterId (unused) */
    0U, /* cryIfKeyId (unused) */
    CRYPTO_PROCESSING_SYNC, /* processingType */
    FALSE, /* callbackUpdateNotification (unused) */
};

static Crypto_JobInfoType TestJobInfo = {
    0U, /* jobId */
    0U, /* jobPriority */
};

static Crypto_JobType TestJob = {
    0U, /* jobId */
    CRYPTO_JOBSTATE_IDLE, /* jobState */
    {
        NULL_PTR, /* inputPtr */
        0U, /* inputLength */
        NULL_PTR, /* secondaryInputPtr */
        0U, /* secondaryInputLength */
        NULL_PTR, /* tertiaryInputPtr */
        0U, /* tertiaryInputLength */
        NULL_PTR, /* outputPtr */
        NULL_PTR, /* outputLengthPtr */
        NULL_PTR, /* secondaryOutputPtr */
        NULL_PTR, /* secondaryOutputLengthPtr */
        0U, /* input64 */
        NULL_PTR, /* verifyPtr */
        NULL_PTR, /* output64Ptr */
        CRYPTO_OPERATIONMODE_SINGLECALL /* mode */
    }, /* jobPrimitiveInputOutput */
    &TestJobPrimitiveInfo, /* jobPrimitiveInfo */
    &TestJobInfo, /* jobInfo */
    CryptoConf_CryptoKey_TestKey_Unused, /* cryptoKeyId */
};

void RNG_TestSuite(void)
{
    uint8 TestOutput_0[32] = {0U};
    uint8 Seed[16] = {
        0xBDU, 0x54U, 0x9EU, 0x98U,
        0x71U, 0x18U, 0xE0U, 0x0CU,
        0xDAU, 0x37U, 0x43U, 0x22U,
        0x51U, 0x81U, 0x27U, 0x38U
    };

    Crypto_ProcessingType Processing;
    Crypto_OperationModeType OpMode;
    uint32 OutputLength;
    uint32 KeyId;
    uint32 ObjectId;
    uint8 DoInit;

    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&Processing, 8);
    TestHarness_PrepareInput((void *)&OutputLength, 32);
    TestHarness_PrepareInput((void *)&OpMode, 8);
    TestHarness_PrepareInput((void *)&KeyId, 32);
    TestHarness_PrepareInput((void *)&ObjectId, 32);

    /* set up output buffer */
    TestJob.jobPrimitiveInputOutput.outputPtr = &TestOutput_0[0];
    TestJob.jobPrimitiveInputOutput.outputLengthPtr = &OutputLength;
    TestJob.jobPrimitiveInfo->processingType = Processing;

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    Crypto_RandomSeed(KeyId, &Seed[0], 16U);

    TestJob.jobPrimitiveInputOutput.mode = OpMode;
    Crypto_ProcessJob(ObjectId, &TestJob);
}

/*=============== END OF FILE RNG_TestSuite.c ================*/